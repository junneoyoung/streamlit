
# import streamlit as st

# st.title('hi')

import React, { useState, useEffect } from 'react';

// 채팅 로직을 위한 커스텀 훅
function useChat() {
    const [messages, setMessages] = useState([]);
    const [ws, setWs] = useState(null);

    useEffect(() => {
        // WebSocket 연결
        const websocket = new WebSocket('ws://your-websocket-server.com');
        setWs(websocket);

        websocket.onmessage = (event) => {
            // 서버로부터 메시지를 받으면 messages 상태 업데이트
            const message = JSON.parse(event.data);
            setMessages((prevMessages) => [...prevMessages, message]);
        };

        // 컴포넌트 언마운트 시 WebSocket 연결 종료
        return () => {
            websocket.close();
        };
    }, []);

    const sendMessage = (message) => {
        // 서버로 메시지 전송
        if (ws) {
            ws.send(JSON.stringify(message));
        }
    };

    return { messages, sendMessage };
}

// 채팅 UI 컴포넌트
function Chat() {
    const { messages, sendMessage } = useChat();
    const [newMessage, setNewMessage] = useState('');

    const handleNewMessageChange = (event) => {
        setNewMessage(event.target.value);
    };

    const handleSendMessage = () => {
        sendMessage({ text: newMessage });
        setNewMessage('');
    };

    return (
        <div>
            <h2>Chat</h2>
            <div className="messages">
                {messages.map((message, index) => (
                    <div key={index}>{message.text}</div>
                ))}
            </div>
            <textarea
                value={newMessage}
                onChange={handleNewMessageChange}
                placeholder="Write message..."
            />
            <button onClick={handleSendMessage}>Send</button>
        </div>
    );
}

// 앱 컴포넌트
function App() {
    return <Chat />;
}

export default App;
