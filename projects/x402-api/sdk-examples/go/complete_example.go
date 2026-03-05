package main

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"sync"
	"time"
)

// ==================== 数据结构 ====================

// APIResponse API 响应结构
type APIResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Cost    float64     `json:"cost"`
	Error   string      `json:"error,omitempty"`
}

// TranslateRequest 翻译请求
type TranslateRequest struct {
	Text   string `json:"text"`
	Source string `json:"source"`
	Target string `json:"target"`
}

// TranslateData 翻译结果数据
type TranslateData struct {
	TranslatedText string `json:"translated_text"`
	SourceLanguage string `json:"source_language"`
	TargetLanguage string `json:"target_language"`
}

// x402Client x402 API 客户端
type x402Client struct {
	walletKey  string
	baseURL    string
	balance    float64
	totalSpent float64
	mu         sync.Mutex
}

// NewClient 创建新客户端
func NewClient(walletKey, baseURL string) *x402Client {
	if baseURL == "" {
		baseURL = "http://localhost:5002"
	}
	return &x402Client{
		walletKey:  walletKey,
		baseURL:    baseURL,
		balance:    10.0, // 模拟初始余额
		totalSpent: 0.0,
	}
}

// generateSignature 生成支付签名
func (c *x402Client) generateSignature(amount float64, endpoint string, timestamp int64) string {
	data := fmt.Sprintf("%.6f:%s:%d", amount, endpoint, timestamp)
	h := hmac.New(sha256.New, []byte(c.walletKey))
	h.Write([]byte(data))
	return hex.EncodeToString(h.Sum(nil))
}

// callAPI 通用 API 调用方法
func (c *x402Client) callAPI(endpoint string, payload interface{}, cost float64) (*APIResponse, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	// 检查余额
	if c.balance < cost {
		return nil, fmt.Errorf("余额不足：需要 %.2f USDC，当前 %.2f USDC", cost, c.balance)
	}

	// 准备请求
	timestamp := time.Now().UnixNano() / 1e6 // 毫秒时间戳
	signature := c.generateSignature(cost, endpoint, timestamp)

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", c.baseURL+"/api/v1/"+endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}

	// 设置支付头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Payment-Amount", strconv.FormatInt(int64(cost*1000000), 10))
	req.Header.Set("X-Payment-Token", "USDC")
	req.Header.Set("X-Payment-Signature", signature)
	req.Header.Set("X-Payment-Timestamp", strconv.FormatInt(timestamp, 10))

	// 发送请求
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API 错误：%d %s", resp.StatusCode, resp.Status)
	}

	var result APIResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	// 扣减余额
	c.balance -= cost
	c.totalSpent += cost
	result.Cost = cost

	return &result, nil
}

// Translate 翻译 API
func (c *x402Client) Translate(text, source, target string) (*APIResponse, error) {
	payload := TranslateRequest{
		Text:   text,
		Source: source,
		Target: target,
	}
	return c.callAPI("translator", payload, 0.02)
}

// CodeGen 代码生成 API
func (c *x402Client) CodeGen(prompt, language string) (*APIResponse, error) {
	payload := map[string]string{
		"prompt":   prompt,
		"language": language,
	}
	return c.callAPI("code-gen", payload, 0.08)
}

// BatchTranslate 批量翻译（享受折扣）
func (c *x402Client) BatchTranslate(texts []TranslateRequest, discount float64) ([]*APIResponse, error) {
	results := make([]*APIResponse, 0, len(texts))
	costPerCall := 0.02 * discount

	for _, task := range texts {
		result, err := c.callAPI("translator", task, costPerCall)
		if err != nil {
			results = append(results, &APIResponse{
				Success: false,
				Error:   err.Error(),
				Cost:    0,
			})
		} else {
			results = append(results, result)
		}
	}

	return results, nil
}

// GetUsageStats 获取使用统计
func (c *x402Client) GetUsageStats() map[string]interface{} {
	c.mu.Lock()
	defer c.mu.Unlock()

	usageRate := (c.totalSpent / 10.0) * 100

	return map[string]interface{}{
		"initial_balance": 10.0,
		"current_balance": c.balance,
		"total_spent":     c.totalSpent,
		"usage_rate":      fmt.Sprintf("%.1f%%", usageRate),
	}
}

// ==================== 使用示例 ====================

func exampleBasicUsage() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 1: 基础调用")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")

	result, err := client.Translate("Hello, world!", "en", "zh")
	if err != nil {
		fmt.Printf("❌ 错误：%v\n", err)
	} else {
		data := result.Data.(map[string]interface{})
		fmt.Printf("✅ 翻译成功：%v\n", data["translated_text"])
		fmt.Printf("💰 花费：%.2f USDC\n\n", result.Cost)
	}
}

func exampleErrorHandling() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 2: 错误处理")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")
	client.balance = 0.01 // 余额不足

	_, err := client.Translate("Hello", "en", "zh")
	if err != nil {
		fmt.Printf("⚠️ 错误：%v\n", err)
		fmt.Println("💡 建议：检查余额或充值\n")
	}
}

func exampleBatchProcessing() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 3: 批量调用（享受折扣）")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")

	// 准备 15 条翻译任务
	texts := make([]TranslateRequest, 15)
	for i := 0; i < 15; i++ {
		texts[i] = TranslateRequest{
			Text:   fmt.Sprintf("Message %d", i),
			Source: "en",
			Target: "zh",
		}
	}

	results, err := client.BatchTranslate(texts, 0.8) // 8 折
	if err != nil {
		fmt.Printf("❌ 错误：%v\n", err)
		return
	}

	totalCost := 0.0
	successful := 0
	for _, r := range results {
		if r.Success {
			totalCost += r.Cost
			successful++
		}
	}

	fmt.Printf("📊 批量翻译 %d/%d 条\n", successful, len(texts))
	fmt.Printf("💰 总花费：%.4f USDC\n", totalCost)
	fmt.Printf("🎯 平均每次：%.4f USDC\n", totalCost/float64(successful))
	fmt.Printf("💡 节省了：%.4f USDC\n\n", 0.02*15-totalCost)
}

func exampleConcurrentCalls() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 4: 并发调用")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")

	// 并发执行
	var wg sync.WaitGroup
	results := make(chan *APIResponse, 5)

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			result, _ := client.Translate(fmt.Sprintf("Text %d", n), "en", "zh")
			results <- result
		}(i)
	}

	wg.Wait()
	close(results)

	successful := 0
	totalCost := 0.0
	for r := range results {
		if r.Success {
			successful++
			totalCost += r.Cost
		}
	}

	fmt.Printf("✅ 成功：%d/%d\n", successful, 5)
	fmt.Printf("💰 总花费：%.4f USDC\n", totalCost)
	fmt.Printf("⚡ 并发执行，节省时间\n\n")
}

func exampleUsageMonitoring() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 5: 使用量监控")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")

	// 模拟使用
	for i := 0; i < 10; i++ {
		client.Translate(fmt.Sprintf("Test %d", i), "en", "zh")
	}

	stats := client.GetUsageStats()

	fmt.Println("📊 使用统计:")
	fmt.Printf("  初始余额：$%.2f USDC\n", stats["initial_balance"])
	fmt.Printf("  当前余额：$%.2f USDC\n", stats["current_balance"])
	fmt.Printf("  总花费：$%.2f USDC\n", stats["total_spent"])
	fmt.Printf("  使用率：%s\n", stats["usage_rate"])

	if stats["current_balance"].(float64) < 2.0 {
		fmt.Println("\n⚠️ 警告：余额低于 $2 USDC，请充值！")
	}

	fmt.Println()
}

func exampleRealWorldApp() {
	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("示例 6: 真实应用 - 多语言客服系统")
	fmt.Println("=" + string(make([]byte, 50)))

	client := NewClient("your_wallet_key", "")

	conversations := []struct {
		User string
		Lang string
	}{
		{"Hello, I need help", "en"},
		{"Bonjour, j'ai un problème", "fr"},
		{"Hola, necesito ayuda", "es"},
	}

	fmt.Println("🎧 客服系统启动...\n")

	for _, conv := range conversations {
		result, err := client.Translate(conv.User, conv.Lang, "zh")
		if err != nil {
			fmt.Printf("❌ 错误：%v\n", err)
			continue
		}

		if result.Success {
			data := result.Data.(map[string]interface{})
			fmt.Printf("[%s] 用户：%s\n", conv.Lang, conv.User)
			fmt.Printf("[zh] 翻译：%v\n", data["translated_text"])
			fmt.Printf("💰 花费：%.2f USDC\n\n", result.Cost)
		}
	}

	fmt.Printf("💵 总成本：$%.2f USDC\n", client.totalSpent)
	fmt.Println("💡 如果自建翻译团队：约 $50/小时")
	fmt.Printf("🎯 使用 x402 API: $%.2f USDC\n", client.totalSpent)
	fmt.Printf("✅ 节省了：$%.2f USDC\n\n", 50-client.totalSpent)
}

func main() {
	fmt.Println("\n🚀 x402 API Go SDK 完整示例\n")

	exampleBasicUsage()
	exampleErrorHandling()
	exampleBatchProcessing()
	exampleConcurrentCalls()
	exampleUsageMonitoring()
	exampleRealWorldApp()

	fmt.Println("=" + string(make([]byte, 50)))
	fmt.Println("✅ 所有示例运行完成！")
	fmt.Println("=" + string(make([]byte, 50)))
}
