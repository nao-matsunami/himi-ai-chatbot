"""
氷見AI実装ラボ チャットボットサーバー
Claude APIを使用したFAQ対応チャットボット
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
import traceback

app = Flask(__name__)
CORS(app)

# APIキーの確認
api_key = os.environ.get("ANTHROPIC_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key starts with: {api_key[:20] if api_key else 'None'}...")

# Claude APIクライアント
client = anthropic.Anthropic(api_key=api_key)

# システムプロンプト
SYSTEM_PROMPT = """あなたは「氷見AI実装ラボ」のAIアシスタントです。
親しみやすく、丁寧に、お客様のAI導入・活用に関する質問にお答えします。

## 提供サービス

### 1. AIレクチャー（1時間 10,000円〜 + 交通費）
**一般向け**
- ChatGPT、Claude、Geminiなどの基本操作
- 日常業務での活用方法
- プロンプトの書き方

**専門向け**
- 開発者向けAPI連携
- Claude Codeなど開発ツールの使い方
- AI活用のワークフロー構築

形式：オンライン / 対面

### 2. AI環境構築（料金：要相談）
- Claude Code、Cursor等のインストール・設定
- 開発環境の構築
- セットアップ済みPCの販売

### 3. AI活用開発（料金：要相談）
- 業務効率化ツール
- データ可視化アプリ
- Webサービス開発

### 4. AIコンサルティング（料金：要相談）
- マーケティング施策の立案
- ブランディング
- 業務改善提案

### 5. Webサイト制作（料金：要相談）
- コーポレートサイト
- ランディングページ

## 進め方
1. ご相談（無料）- お問い合わせフォームからご連絡
2. ヒアリング - オンラインまたは対面でご要望をお聞きします
3. ご提案・お見積り - 内容と料金をご提示
4. 実施・開発 - 合意後、作業を進めます
5. 納品・サポート - 完了後もフォローアップ可能

## 対応エリア
- オンライン：全国対応
- 対面：富山県（氷見市周辺）

## 回答のガイドライン
- 簡潔で分かりやすい日本語で回答
- 具体的な料金は「要相談」のものは「お見積りします」と伝える
- お問い合わせを促す場合は https://himi-ai-lab.jp/inquiry/ を案内
- 専門用語は避け、初心者にも分かりやすく説明
- 回答は200文字程度を目安に簡潔に
- 不明な点は正直に「詳細はお問い合わせください」と伝える
"""


@app.route("/chat", methods=["POST"])
def chat():
    """チャットエンドポイント"""
    print("=== /chat endpoint called ===")
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        user_message = data.get("message", "")
        conversation_history = data.get("history", [])
        
        if not user_message:
            print("Error: Empty message")
            return jsonify({"error": "メッセージが空です", "success": False}), 400
        
        # 会話履歴を構築
        messages = []
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        print(f"Calling Claude API with {len(messages)} messages")
        
        # Claude APIを呼び出し
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        assistant_message = response.content[0].text
        print(f"Claude response: {assistant_message[:100]}...")
        
        return jsonify({
            "response": assistant_message,
            "success": True
        })
        
    except anthropic.APIError as e:
        print(f"Anthropic API Error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"APIエラー: {str(e)}",
            "success": False
        }), 500
    except Exception as e:
        print(f"General Error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"エラー: {str(e)}",
            "success": False
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """ヘルスチェック"""
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def index():
    """ルート"""
    return jsonify({"message": "Himi AI Chatbot Server", "status": "running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
