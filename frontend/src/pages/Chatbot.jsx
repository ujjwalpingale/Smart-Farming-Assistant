import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export default function Chatbot() {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function sendMessage(text) {
    const msg = text || input;
    if (!msg || !msg.trim()) return;

    const userMsg = { role: 'user', content: msg, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/chatbot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: msg, 
          language: i18n.language 
        }),
      });

      const data = await response.json();
      if (data.response) {
        setMessages(prev => [...prev, { 
          role: 'bot', 
          content: data.response,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: t('chatbot.error') }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: t('common.network_error') }]);
    } finally {
      setLoading(false);
    }
  }

  const startVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Browser does not support Speech Recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = i18n.language === 'mr' ? 'mr-IN' : 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      sendMessage(transcript);
    };

    recognition.start();
  };

  const quickQuestions = [
    t('chatbot.quick_q1'),
    t('chatbot.quick_q2'),
    t('chatbot.quick_q3'),
  ];

  return (
    <div className="main-content">
      <div className="container" style={{ maxWidth: '900px' }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(34, 197, 94, 0.12)', color: 'var(--accent-green)' }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
              <path d="M5 3v4"/><path d="M3 5h4"/>
            </svg>
          </div>
          <div>
            <div className="page-header-title">{t('chatbot.title')}</div>
            <div className="page-header-desc">{t('chatbot.subtitle')}</div>
          </div>
        </div>

        <div className="chat-window animate-fade-up delay-1">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '4rem' }}>
                <div style={{ marginBottom: '1.5rem', color: 'var(--accent-green)', opacity: 0.8 }}>
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto' }}>
                    <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
                  </svg>
                </div>
                <p style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-primary)' }}>{t('chatbot.subtitle')}</p>
                <p className="text-sm mt-2">{t('chatbot.placeholder')}</p>
              </div>
            )}
            
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role === 'user' ? 'message-user' : 'message-bot'}`}>
                {msg.role === 'bot' && (
                  <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-green)', marginBottom: '0.25rem', letterSpacing: '0.05em' }}>
                    SMART ASSISTANT
                  </div>
                )}
                <div style={{ wordBreak: 'break-word' }}>{msg.content}</div>
                <div style={{ 
                  fontSize: '0.65rem', 
                  opacity: 0.6, 
                  textAlign: 'right', 
                  marginTop: '0.4rem',
                  fontWeight: 500
                }}>
                  {msg.time}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message message-bot" style={{ padding: '1rem' }}>
                <div className="spinner" style={{ width: '1.2rem', height: '1.2rem' }} />
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-area">
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              {quickQuestions.map((q, i) => (
                <button 
                  key={i} 
                  className="chat-quick-btn" 
                  onClick={() => sendMessage(q)}
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div className={isListening ? 'voice-pulse' : ''}>
                <button 
                  className={`btn ${isListening ? 'btn-danger' : 'btn-outline'}`}
                  style={{ borderRadius: '50%', width: '48px', height: '48px', padding: 0 }}
                  onClick={startVoice}
                  disabled={loading}
                  title={isListening ? t('chatbot.voice_stop') : t('chatbot.voice_start')}
                >
                  {isListening ? '🛑' : '🎤'}
                </button>
              </div>
              
              <div style={{ flex: 1, position: 'relative' }}>
                <input 
                  className="form-input" 
                  style={{ borderRadius: 'var(--radius-xl)', paddingRight: '4rem' }}
                  placeholder={t('chatbot.placeholder')}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
              </div>

              <button 
                className="btn btn-primary"
                style={{ borderRadius: 'var(--radius-xl)', padding: '0.7rem 1.5rem' }}
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
              >
                {t('common.submit')}
              </button>
            </div>
          </div>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-secondary text-sm" style={{ textDecoration: 'none' }}>
            ← {t('common.back_home')}
          </Link>
        </div>
      </div>
    </div>
  );
}
