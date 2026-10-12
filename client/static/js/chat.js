document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('new_message', function(m) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        const emptyDiv = container.querySelector('.empty');
        if (emptyDiv) emptyDiv.remove();

        container.insertAdjacentHTML('beforeend', `
            <div style="background: #121620; border: 1px solid var(--line); padding: 12px; border-radius: var(--radius);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: var(--accent);">${m.username}</span>
                    <span style="font-size: 11px; color: var(--muted);">${m.timestamp}</span>
                </div>
                <p style="word-break: break-word;">${m.content}</p>
            </div>
        `);
        container.scrollTop = container.scrollHeight;
    });

    window.sendChatMessage = function() {
        const input = document.getElementById('chatInput');
        if (!input) return;
        const content = input.value.trim();
        if (!content) return;

        socket.emit('send_message', { content: content });
        input.value = '';
    };

    window.handleKeyPress = function(event) {
        if (event.key === 'Enter') {
            sendChatMessage();
        }
    };

    fetch('/api/chat')
        .then(res => res.json())
        .then(messages => {
            const container = document.getElementById('chatMessages');
            if (!container) return;
            
            if (messages.length === 0) {
                container.innerHTML = '<div class="empty">No messages yet. Start the conversation below!</div>';
                return;
            }
            container.innerHTML = messages.map(m => `
                <div style="background: #121620; border: 1px solid var(--line); padding: 12px; border-radius: var(--radius);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: var(--accent);">${m.username}</span>
                        <span style="font-size: 11px; color: var(--muted);">${m.timestamp}</span>
                    </div>
                    <p style="word-break: break-word;">${m.content}</p>
                </div>
            `).join('');
            container.scrollTop = container.scrollHeight;
        });
});