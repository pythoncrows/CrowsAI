async function fetchMessages() {
  const res = await fetch('/api/chat/list');
  if (!res.ok) {
    document.getElementById('chatbox').innerText = 'Failed to load messages';
    return;
  }
  const data = await res.json();
  const chatbox = document.getElementById('chatbox');
  chatbox.innerHTML = '';
  (data.messages || []).forEach(m => {
    const el = document.createElement('div');
    el.className = 'msg';
    el.innerHTML = `<div class="meta">${m.user} — ${m.timestamp_utc}</div><div>${escapeHtml(m.message)}</div>`;
    chatbox.appendChild(el);
  });
  chatbox.scrollTop = chatbox.scrollHeight;
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/[&<>"']/g, function(c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
  });
}

document.getElementById('send').addEventListener('click', async () => {
  const user = document.getElementById('user').value || 'Guest';
  const message = document.getElementById('message').value || '';
  if (!message.trim()) return alert('Message empty');
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user, message })
  });
  if (res.ok) {
    document.getElementById('message').value = '';
    await fetchMessages();
  } else {
    const err = await res.json().catch(()=>({error:'Unknown'}));
    alert('Send failed: ' + (err.error || JSON.stringify(err)));
  }
});

// initial load
fetchMessages();
// optional: auto-refresh every 5 seconds
setInterval(fetchMessages, 5000);
