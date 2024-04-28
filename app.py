import streamlit as st
import requests

def analyze_sentiment(text, api_key, endpoint):
    url = f"{endpoint}/text/analytics/v3.0/sentiment"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "documents": [
            {"id": "1", "text": text}
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result['documents'][0]['sentiment']
    else:
        return None

def main():
    st.title("Azure Text Analytics API Sentiment Analysis")
    
    # Azure Text Analytics API 정보 입력
    api_key = st.text_input("Enter your Azure API Key:")
    endpoint = st.text_input("Enter your Azure Text Analytics endpoint:")
    
    # 텍스트 입력
    text = st.text_area("Enter the text to analyze:")
    
    # 감정 분석 실행
    if st.button("Analyze Sentiment"):
        if api_key and endpoint and text:
            sentiment = analyze_sentiment(text, api_key, endpoint)
            if sentiment:
                st.write(f"Sentiment: {sentiment}")
            else:
                st.error("Failed to analyze sentiment. Please check your API key and endpoint.")
        else:
            st.error("Please enter your Azure API key, endpoint, and the text to analyze.")

if __name__ == "__main__":
    main()
