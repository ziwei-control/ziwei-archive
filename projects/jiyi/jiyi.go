package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// 配置
const (
	JiyiDir      = "/home/admin/Ziwei/jiyi"
	MemoryDir    = JiyiDir + "/memory"
	IndexFile    = JiyiDir + "/index.json"
	Version      = "1.0.0"
)

// 记忆结构
type Memory struct {
	ID        string    `json:"id"`
	Category  string    `json:"category"`
	Content   string    `json:"content"`
	Tags      []string  `json:"tags"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	IsNew     bool      `json:"is_new"`
}

// 索引结构
type Index struct {
	Categories map[string][]string `json:"categories"`
	Tags       map[string][]string `json:"tags"`
	LastUpdate time.Time           `json:"last_update"`
}

// 颜色定义
const (
	ColorReset  = "\033[0m"
	ColorRed    = "\033[31m"
	ColorGreen  = "\033[32m"
	ColorYellow = "\033[33m"
	ColorBlue   = "\033[34m"
	ColorPurple = "\033[35m"
	ColorCyan   = "\033[36m"
)

func main() {
	if len(os.Args) < 2 {
		showHelp()
		return
	}

	command := os.Args[1]

	switch command {
	case "add", "a":
		handleAdd(os.Args[2:])
	case "search", "s", "find":
		handleSearch(os.Args[2:])
	case "list", "ls":
		handleList(os.Args[2:])
	case "categories", "cat":
		handleCategories()
	case "tags":
		handleTags()
	case "version", "v", "-v", "--version":
		showVersion()
	case "help", "h", "-h", "--help":
		showHelp()
	default:
		// 默认搜索
		handleSearch(os.Args[1:])
	}
}

func showHelp() {
	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          jiyi - 紫微智控记忆命令                        ║%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()
	fmt.Printf("%s用法:%s\n", ColorCyan, ColorReset)
	fmt.Println("  jiyi <命令> [参数]")
	fmt.Println()
	fmt.Printf("%s命令:%s\n", ColorCyan, ColorReset)
	fmt.Println("  add, a <内容> [分类] [标签...]  - 添加记忆")
	fmt.Println("  search, s, find <关键词>       - 搜索记忆")
	fmt.Println("  list, ls [分类]                - 列出记忆")
	fmt.Println("  categories, cat                - 显示所有分类")
	fmt.Println("  tags                           - 显示所有标签")
	fmt.Println("  version, v                     - 显示版本")
	fmt.Println("  help, h                        - 显示帮助")
	fmt.Println()
	fmt.Printf("%s示例:%s\n", ColorCyan, ColorReset)
	fmt.Println("  jiyi add \"runtask 命令用于启动任务\" 命令 runtask 自动化")
	fmt.Println("  jiyi search runtask")
	fmt.Println("  jiyi list 命令")
	fmt.Println("  jiyi")
	fmt.Println()
}

func showVersion() {
	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          jiyi - 紫微智控记忆命令                        ║%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()
	fmt.Printf("%s版本:%s v%s\n", ColorCyan, ColorReset, Version)
	fmt.Printf("%s日期:%s 2026-02-28\n", ColorCyan, ColorReset)
	fmt.Printf("%s代号:%s 紫微智控 - 记忆命令\n", ColorCyan, ColorReset)
	fmt.Println()
	fmt.Printf("%s功能:%s\n", ColorCyan, ColorReset)
	fmt.Println("  ✅ 分门别类存储")
	fmt.Println("  ✅ 最小存储空间")
	fmt.Println("  ✅ 快速搜索")
	fmt.Println("  ✅ 自动分类")
	fmt.Println("  ✅ 新旧记忆分离")
	fmt.Println()
}

func initJiyi() {
	// 创建目录
	os.MkdirAll(JiyiDir, 0755)
	os.MkdirAll(MemoryDir, 0755)

	// 初始化索引
	if _, err := os.Stat(IndexFile); os.IsNotExist(err) {
		index := Index{
			Categories: make(map[string][]string),
			Tags:       make(map[string][]string),
			LastUpdate: time.Now(),
		}
		saveIndex(index)
	}
}

func loadIndex() Index {
	data, err := os.ReadFile(IndexFile)
	if err != nil {
		return Index{
			Categories: make(map[string][]string),
			Tags:       make(map[string][]string),
			LastUpdate: time.Now(),
		}
	}

	var index Index
	json.Unmarshal(data, &index)
	return index
}

func saveIndex(index Index) {
	data, _ := json.MarshalIndent(index, "", "  ")
	os.WriteFile(IndexFile, data, 0644)
}

func loadMemory(id string) *Memory {
	filePath := filepath.Join(MemoryDir, id+".json")
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil
	}

	var memory Memory
	json.Unmarshal(data, &memory)
	return &memory
}

func saveMemory(memory Memory) {
	data, _ := json.MarshalIndent(memory, "", "  ")
	filePath := filepath.Join(MemoryDir, memory.ID+".json")
	os.WriteFile(filePath, data, 0644)
}

func generateID() string {
	return fmt.Sprintf("m_%d", time.Now().UnixNano())
}

func autoCategory(content string) string {
	content = strings.ToLower(content)

	// 自动分类关键词
	categories := map[string][]string{
		"命令":     {"命令", "runtask", "look", "jiyi", "执行"},
		"项目":     {"项目", "仓库", "github", "gitee"},
		"配置":     {"配置", "config", "env", "token"},
		"流程":     {"流程", "步骤", "自动", "同步"},
		"错误":     {"错误", "失败", "问题", "bug"},
		"系统":     {"系统", "服务", "监控", "进程"},
		"文档":     {"文档", "说明", "readme", "sop"},
	}

	for cat, keywords := range categories {
		for _, kw := range keywords {
			if strings.Contains(content, kw) {
				return cat
			}
		}
	}

	return "其他"
}

func handleAdd(args []string) {
	if len(args) < 1 {
		fmt.Printf("%s✗ 请提供记忆内容%s\n", ColorRed, ColorReset)
		fmt.Println("用法：jiyi add <内容> [分类] [标签...]")
		return
	}

	initJiyi()

	content := args[0]
	category := "其他"
	tags := []string{}

	// 解析分类和标签
	if len(args) > 1 {
		category = args[1]
		if len(args) > 2 {
			tags = args[2:]
		}
	} else {
		// 自动分类
		category = autoCategory(content)
	}

	memory := Memory{
		ID:        generateID(),
		Category:  category,
		Content:   content,
		Tags:      tags,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IsNew:     true,
	}

	saveMemory(memory)

	// 更新索引
	index := loadIndex()
	index.Categories[category] = append(index.Categories[category], memory.ID)
	for _, tag := range tags {
		index.Tags[tag] = append(index.Tags[tag], memory.ID)
	}
	index.LastUpdate = time.Now()
	saveIndex(index)

	fmt.Printf("%s✓ 记忆已添加%s\n", ColorGreen, ColorReset)
	fmt.Printf("  ID: %s\n", memory.ID)
	fmt.Printf("  分类：%s\n", memory.Category)
	fmt.Printf("  标签：%v\n", memory.Tags)
	fmt.Printf("  时间：%s\n", memory.CreatedAt.Format("2006-01-02 15:04:05"))
}

func handleSearch(args []string) {
	if len(args) < 1 {
		// 无参数进入交互模式
		interactiveSearch()
		return
	}

	initJiyi()

	keyword := strings.Join(args, " ")
	keyword = strings.ToLower(keyword)

	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          搜索结果：%s%-40s%s%s\n", ColorBlue, ColorCyan, keyword, ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()

	count := 0
	index := loadIndex()

	// 搜索所有记忆
	for _, ids := range index.Categories {
		for _, id := range ids {
			memory := loadMemory(id)
			if memory == nil {
				continue
			}

			content := strings.ToLower(memory.Content)
			tags := strings.ToLower(strings.Join(memory.Tags, " "))
			category := strings.ToLower(memory.Category)

			if strings.Contains(content, keyword) ||
				strings.Contains(tags, keyword) ||
				strings.Contains(category, keyword) {

				count++
				printMemory(memory, count)
			}
		}
	}

	if count == 0 {
		fmt.Printf("%s✗ 未找到相关记忆%s\n", ColorYellow, ColorReset)
		fmt.Println()
		fmt.Printf("%s建议:%s\n", ColorCyan, ColorReset)
		fmt.Printf("  1. 检查关键词是否正确\n")
		fmt.Printf("  2. 尝试其他关键词\n")
		fmt.Printf("  3. 添加新记忆：jiyi add \"内容\" 分类 标签\n")
		fmt.Println()

		// 询问是否添加新记忆
		fmt.Printf("%s是否添加为新记忆？(y/n): %s", ColorCyan, ColorReset)
		reader := bufio.NewReader(os.Stdin)
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		if input == "y" || input == "Y" {
			fmt.Printf("输入记忆内容：")
			content, _ := reader.ReadString('\n')
			content = strings.TrimSpace(content)

			if content != "" {
				// 自动分类并添加
				category := autoCategory(content)
				fmt.Printf("自动分类：%s\n", category)
				fmt.Printf("输入标签（空格分隔）：")
				tagInput, _ := reader.ReadString('\n')
				tags := strings.Fields(strings.TrimSpace(tagInput))

				// 调用 add
				args := append([]string{content, category}, tags...)
				handleAdd(args)
			}
		}
	} else {
		fmt.Printf("%s找到 %d 条记忆%s\n", ColorGreen, count, ColorReset)
	}
}

func interactiveSearch() {
	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          jiyi - 交互式搜索                             ║%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()
	fmt.Printf("%s输入关键词搜索（输入 q 退出）:%s\n", ColorCyan, ColorReset)

	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Printf("\n%s> %s", ColorGreen, ColorReset)
		input, err := reader.ReadString('\n')
		if err != nil {
			break
		}

		input = strings.TrimSpace(input)
		if input == "q" || input == "quit" {
			break
		}

		if input != "" {
			handleSearch([]string{input})
		}
	}
}

func handleList(args []string) {
	initJiyi()

	category := ""
	if len(args) > 0 {
		category = args[0]
	}

	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	if category != "" {
		fmt.Printf("%s║          记忆列表 - %s%-34s%s%s\n", ColorBlue, ColorCyan, category, ColorBlue, ColorReset)
	} else {
		fmt.Printf("%s║          记忆列表 - 全部%s%15s%s\n", ColorBlue, ColorCyan, ColorBlue, ColorReset)
	}
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()

	index := loadIndex()
	count := 0

	if category != "" {
		// 列出指定分类
		ids, ok := index.Categories[category]
		if !ok {
			fmt.Printf("%s✗ 分类不存在：%s%s\n", ColorRed, ColorCyan, category, ColorReset)
			return
		}

		for _, id := range ids {
			memory := loadMemory(id)
			if memory != nil {
				count++
				printMemory(memory, count)
			}
		}
	} else {
		// 列出所有
		for cat, ids := range index.Categories {
			fmt.Printf("%s【%s】%s\n", ColorPurple, cat, ColorReset)

			for _, id := range ids {
				memory := loadMemory(id)
				if memory != nil {
					count++
					fmt.Printf("  %s\n", memory.Content)
					if memory.IsNew {
						fmt.Printf("    %s[NEW]%s\n", ColorGreen, ColorReset)
					}
					fmt.Println()
				}
			}
		}
	}

	if count == 0 {
		fmt.Printf("%s✗ 没有记忆%s\n", ColorYellow, ColorReset)
	} else {
		fmt.Printf("%s共 %d 条记忆%s\n", ColorGreen, count, ColorReset)
	}
}

func handleCategories() {
	initJiyi()

	index := loadIndex()

	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          记忆分类                                      ║%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()

	for cat, ids := range index.Categories {
		fmt.Printf("  %s%-15s%s %d 条记忆\n", ColorPurple, cat, ColorReset, len(ids))
	}

	fmt.Println()
	fmt.Printf("总计：%d 个分类\n", len(index.Categories))
}

func handleTags() {
	initJiyi()

	index := loadIndex()

	fmt.Printf("%s╔════════════════════════════════════════════════════════╗%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s║          记忆标签                                      ║%s\n", ColorBlue, ColorReset)
	fmt.Printf("%s╚════════════════════════════════════════════════════════╝%s\n", ColorBlue, ColorReset)
	fmt.Println()

	for tag, ids := range index.Tags {
		fmt.Printf("  %s#%-15s%s %d 条记忆\n", ColorCyan, tag, ColorReset, len(ids))
	}

	fmt.Println()
	fmt.Printf("总计：%d 个标签\n", len(index.Tags))
}

func printMemory(memory Memory, index int) {
	fmt.Printf("%s【记忆 #%d】%s\n", ColorPurple, index, ColorReset)
	fmt.Printf("  内容：%s\n", memory.Content)
	fmt.Printf("  分类：%s\n", memory.Category)
	if len(memory.Tags) > 0 {
		fmt.Printf("  标签：%v\n", memory.Tags)
	}
	fmt.Printf("  时间：%s\n", memory.CreatedAt.Format("2006-01-02 15:04:05"))
	if memory.IsNew {
		fmt.Printf("  %s[新记忆]%s\n", ColorGreen, ColorReset)
	}
	fmt.Printf("  文件：%s.json\n", memory.ID)
	fmt.Println()
}
