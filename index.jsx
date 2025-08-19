import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import Chart from 'chart.js/auto';
import 'tailwindcss/tailwind.css';

const App = () => {
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [token, setToken] = useState(localStorage.getItem('token') || '');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoggedIn, setIsLoggedIn] = useState(!!token);
    const [language, setLanguage] = useState('en');
    const [moodData, setMoodData] = useState([]);
    const chatBoxRef = useRef(null);
    const chartRef = useRef(null);
    const myChart = useRef(null);

    const sendMessage = async () => {
        if (!message.trim()) return;
        const newChat = { sender: 'user', text: message };
        setChat([...chat, newChat]);
        setMessage('');

    const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message, language })
    });
    const data = await res.json();
    setChat([...chat, newChat, { sender: 'bot', text: data.response, sentiment: data.sentiment, confidence: data.confidence }]);
    if (chatBoxRef.current) chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
};

  const handleLogin = async () => {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.access_token) {
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      setIsLoggedIn(true);
    }
  };

  const handleRegister = async () => {
    const res = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (res.ok) alert('Registered successfully! Please log in.');
  };

  const fetchMoodTrend = async () => {
    const res = await fetch('/mood_trend', {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setMoodData(data);
  };

  useEffect(() => {
    if (isLoggedIn) fetchMoodTrend();
  }, [isLoggedIn]);

  
  useEffect(() => {
    if (moodData.length && chartRef.current) {
      if (myChart.current) myChart.current.destroy();
      myChart.current = new Chart(chartRef.current, {
        type: 'line',
        data: {
          labels: moodData.map(d => new Date(d.timestamp).toLocaleDateString()),
          datasets: [{
            label: 'Sentiment Confidence',
            data: moodData.map(d => d.sentiment === 'POSITIVE' ? d.confidence : -d.confidence),
            borderColor: 'rgba(76, 192, 192, 1)',
            fill: false
          }]
        },
        options: { scales: { y: { min: -1, max: 1 } } }
      });
    }
  }, [moodData]);

  return (
    <div className="max-w-4xl mx-auto p-4 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold text-center mb-4">Mental Health Support Platform</h1>
      {!isLoggedIn ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 mb-2 border rounded"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 mb-2 border rounded"
          />
          <div className="flex gap-2">
            <button onClick={handleLogin} className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">LOGIN</button>
            <button onClick={handleRegister} className="bg-green-500 text-white p-2 rounded hover:bg-green-600">Register</button>
          </div>
        </div>
      ) : (
        <div>
          <div className="bg-white p-4 rounded-lg shadow-md mb-4">
            <div ref={chatBoxRef} className="h-96 overflow-y-auto border p-4 mb-4">
              {chat.map((msg, i) => (
                <div key={i} className={`p-2 mb-2 rounded ${msg.sender === 'user' ? 'bg-green-100 text-right' : 'bg-red-100'}`}>
                  {msg.text}
                  {msg.sentiment && <div className="text-sm text-gray-500">Sentiment: {msg.sentiment} ({(msg.confidence * 100).toFixed(0)}%)</div>}
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <select value={language} onChange={(e) => setLanguage(e.target.value)} className="p-2 border rounded">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
              </select>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 p-2 border rounded"
              />
              <button onClick={sendMessage} className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">SEND</button>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-2">Mood Trend</h2>
            <canvas ref={chartRef}></canvas>
          </div>
        </div>
      )}
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));