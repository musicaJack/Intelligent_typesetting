# 📱 TXT输出格式 - MCU使用指南

本指南详细说明如何在MCU（如RP2040）上使用智能排版系统生成的TXT文件。

## 📋 概述

TXT输出格式专为MCU设备优化，包含结构化标签，支持快速检索和定位。相比JSON格式，TXT格式具有以下优势：

- **轻量化**: 文件大小减少90%以上
- **快速检索**: 结构化标签支持O(1)时间复杂度的定位
- **内存友好**: 适合小内存设备（如RP2040的264KB RAM）
- **直接渲染**: 无需解析，可直接显示

## 🏷️ 标签格式

### 页面标签
```
<PAGE_001_START>  # 第1页开始
<PAGE_001_END>    # 第1页结束
<PAGE_002_START>  # 第2页开始
<PAGE_002_END>    # 第2页结束
```

**注意**: 所有页面都包含完整的开始和结束标签，便于MCU统一处理。

### 行标签
```
<LINE_001_01> 弗农·德思札先生在一
<LINE_001_02> 家名叫格朗宁的公司做
<LINE_001_03> 主管，公司生产钻机。
```

### 标签格式说明
- `PAGE_XXX_START/END`: 页面开始/结束标签，XXX为3位页码
- `LINE_XXX_YY`: 行标签，XXX为3位页码，YY为2位行号
- 标签格式固定，便于MCU快速识别和解析

## 🔧 MCU API接口

### C语言接口（适用于RP2040）

#### 1. 文件结构定义
```c
// 页面信息结构
typedef struct {
    uint16_t page_id;
    uint32_t start_offset;
    uint32_t end_offset;
    uint8_t line_count;
} page_info_t;

// 行信息结构
typedef struct {
    uint16_t page_id;
    uint8_t line_id;
    uint32_t offset;
    uint16_t length;
    char text[64];  // 最大64字符
} line_info_t;

// 文件索引结构
typedef struct {
    uint16_t total_pages;
    uint16_t total_lines;
    page_info_t pages[100];  // 最多100页
    line_info_t lines[1000]; // 最多1000行
} file_index_t;
```

#### 2. 核心API函数
```c
// 初始化文件索引
int txt_init_index(const char* filename, file_index_t* index);

// 跳转到指定页面
int txt_goto_page(file_index_t* index, uint16_t page_id);

// 跳转到指定行
int txt_goto_line(file_index_t* index, uint16_t page_id, uint8_t line_id);

// 读取当前页面内容
int txt_read_page(file_index_t* index, uint16_t page_id, char* buffer, uint32_t buffer_size);

// 读取指定行内容
int txt_read_line(file_index_t* index, uint16_t page_id, uint8_t line_id, char* buffer, uint32_t buffer_size);

// 搜索文本（简单字符串匹配）
int txt_search_text(file_index_t* index, const char* search_text, uint16_t* found_page, uint8_t* found_line);

// 获取文件统计信息
void txt_get_stats(file_index_t* index, uint16_t* total_pages, uint16_t* total_lines);
```

#### 3. 实现示例
```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// 标签解析函数
int parse_tag(const char* line, char* tag_type, uint16_t* page_id, uint8_t* line_id) {
    if (strncmp(line, "<PAGE_", 6) == 0) {
        *tag_type = 'P';
        sscanf(line, "<PAGE_%hu_", page_id);
        return 0;
    } else if (strncmp(line, "<LINE_", 6) == 0) {
        *tag_type = 'L';
        sscanf(line, "<LINE_%hu_%hhu>", page_id, line_id);
        return 0;
    }
    return -1;
}

// 初始化文件索引
int txt_init_index(const char* filename, file_index_t* index) {
    FILE* file = fopen(filename, "r");
    if (!file) return -1;
    
    memset(index, 0, sizeof(file_index_t));
    
    char line[256];
    uint32_t offset = 0;
    uint16_t current_page = 0;
    uint8_t current_line = 0;
    
    while (fgets(line, sizeof(line), file)) {
        char tag_type;
        uint16_t page_id;
        uint8_t line_id;
        
        if (parse_tag(line, &tag_type, &page_id, &line_id) == 0) {
            if (tag_type == 'P') {
                if (strstr(line, "_START")) {
                    current_page = page_id;
                    index->pages[page_id-1].page_id = page_id;
                    index->pages[page_id-1].start_offset = offset;
                    index->total_pages++;
                } else if (strstr(line, "_END")) {
                    index->pages[page_id-1].end_offset = offset;
                }
            } else if (tag_type == 'L') {
                line_info_t* line_info = &index->lines[index->total_lines];
                line_info->page_id = page_id;
                line_info->line_id = line_id;
                line_info->offset = offset;
                
                // 提取文本内容
                char* text_start = strchr(line, '>');
                if (text_start) {
                    text_start++; // 跳过'>'
                    strncpy(line_info->text, text_start, sizeof(line_info->text)-1);
                    line_info->text[sizeof(line_info->text)-1] = '\0';
                    line_info->length = strlen(line_info->text);
                }
                
                index->total_lines++;
                index->pages[page_id-1].line_count++;
            }
        }
        offset += strlen(line);
    }
    
    fclose(file);
    return 0;
}
```

## 📱 完整Demo示例

### RP2040 + ST7306屏幕示例

```c
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

// ST7306屏幕配置
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS   17
#define PIN_SCK  18
#define PIN_MOSI 19
#define PIN_DC   20
#define PIN_RST  21

// 文件索引
file_index_t book_index;
uint16_t current_page = 1;
uint8_t current_line = 1;

// 初始化ST7306屏幕
void init_display() {
    spi_init(SPI_PORT, 40000000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS, GPIO_FUNC_SIO);
    gpio_set_function(PIN_DC, GPIO_FUNC_SIO);
    gpio_set_function(PIN_RST, GPIO_FUNC_SIO);
    
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_set_dir(PIN_DC, GPIO_OUT);
    gpio_set_dir(PIN_RST, GPIO_OUT);
    
    // 屏幕初始化代码...
}

// 显示文本行
void display_line(const char* text, uint8_t line_num) {
    // 清除指定行
    clear_line(line_num);
    
    // 显示文本
    draw_text(0, line_num * 16, text, 16);
    
    // 刷新屏幕
    refresh_display();
}

// 显示当前页面
void display_current_page() {
    char buffer[64];
    
    // 显示页面标题
    snprintf(buffer, sizeof(buffer), "第 %d 页", current_page);
    display_line(buffer, 0);
    
    // 显示页面内容（最多12行）
    for (int i = 0; i < 12 && i < book_index.pages[current_page-1].line_count; i++) {
        line_info_t* line_info = &book_index.lines[book_index.pages[current_page-1].start_offset + i];
        display_line(line_info->text, i + 1);
    }
}

// 按键处理
void handle_button_press(uint8_t button) {
    switch (button) {
        case 0: // 上一页
            if (current_page > 1) {
                current_page--;
                display_current_page();
            }
            break;
            
        case 1: // 下一页
            if (current_page < book_index.total_pages) {
                current_page++;
                display_current_page();
            }
            break;
            
        case 2: // 跳转到指定页面
            // 实现页面跳转逻辑
            break;
            
        case 3: // 搜索功能
            // 实现搜索逻辑
            break;
    }
}

// 主函数
int main() {
    stdio_init_all();
    
    // 初始化屏幕
    init_display();
    
    // 初始化文件索引
    if (txt_init_index("book.txt", &book_index) != 0) {
        printf("Failed to load book index\n");
        return -1;
    }
    
    printf("Book loaded: %d pages, %d lines\n", 
           book_index.total_pages, book_index.total_lines);
    
    // 显示第一页
    display_current_page();
    
    // 主循环
    while (true) {
        // 检测按键
        if (gpio_get(22)) { // 按钮1
            handle_button_press(0);
            sleep_ms(200);
        }
        if (gpio_get(23)) { // 按钮2
            handle_button_press(1);
            sleep_ms(200);
        }
        
        sleep_ms(10);
    }
    
    return 0;
}
```

### 搜索功能实现

```c
// 简单文本搜索
int search_text(const char* search_text, uint16_t* found_page, uint8_t* found_line) {
    for (int i = 0; i < book_index.total_lines; i++) {
        line_info_t* line_info = &book_index.lines[i];
        if (strstr(line_info->text, search_text)) {
            *found_page = line_info->page_id;
            *found_line = line_info->line_id;
            return 0;
        }
    }
    return -1; // 未找到
}

// 使用示例
void demo_search() {
    uint16_t page;
    uint8_t line;
    
    if (search_text("德思札", &page, &line) == 0) {
        printf("找到文本在第%d页第%d行\n", page, line);
        
        // 跳转到找到的位置
        current_page = page;
        current_line = line;
        display_current_page();
    } else {
        printf("未找到指定文本\n");
    }
}
```

## 📊 性能优化建议

### 内存优化
1. **索引缓存**: 将文件索引存储在Flash中，避免重复解析
2. **分页加载**: 只加载当前页面到内存
3. **文本缓存**: 缓存最近访问的几行文本

### 速度优化
1. **标签预解析**: 启动时一次性解析所有标签
2. **二分查找**: 使用二分查找快速定位页面
3. **直接跳转**: 利用标签偏移量直接跳转

### 存储优化
```c
// 压缩的索引结构（节省内存）
typedef struct {
    uint16_t page_id;
    uint32_t offset;
    uint8_t line_count;
} compact_page_info_t;

// 使用示例
compact_page_info_t pages[100];
```

## 🔧 调试工具

### 标签验证工具
```c
// 验证TXT文件标签完整性
int validate_tags(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) return -1;
    
    char line[256];
    uint16_t page_count = 0;
    uint16_t line_count = 0;
    uint16_t current_page = 0;
    
    while (fgets(line, sizeof(line), file)) {
        if (strstr(line, "<PAGE_") && strstr(line, "_START")) {
            page_count++;
            sscanf(line, "<PAGE_%hu_", &current_page);
        } else if (strstr(line, "<LINE_")) {
            line_count++;
        }
    }
    
    printf("验证结果: %d页, %d行\n", page_count, line_count);
    fclose(file);
    return 0;
}
```

## 📝 使用注意事项

1. **文件编码**: 确保TXT文件使用UTF-8编码
2. **内存限制**: RP2040只有264KB RAM，注意内存使用
3. **标签格式**: 严格按照标签格式，避免解析错误
4. **错误处理**: 添加适当的错误处理机制
5. **文件大小**: 建议单个文件不超过1MB

## 🚀 扩展功能

### 书签功能
```c
// 保存书签
void save_bookmark(uint16_t page, uint8_t line) {
    // 保存到Flash或EEPROM
}

// 加载书签
void load_bookmark(uint16_t* page, uint8_t* line) {
    // 从Flash或EEPROM加载
}
```

### 阅读进度
```c
// 计算阅读进度
float get_reading_progress() {
    return (float)current_page / book_index.total_pages * 100.0f;
}
```

### 字体支持
```c
// 支持不同字体大小
typedef enum {
    FONT_SMALL = 12,
    FONT_MEDIUM = 16,
    FONT_LARGE = 20
} font_size_t;

void set_font_size(font_size_t size);
```

---

📖 **更多信息**: 参考主项目 [README.md](README.md) 了解完整的智能排版系统功能。 