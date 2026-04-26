import { useState, useEffect, useContext, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getGroup, getMessages, sendMessage, getMaterials, uploadMaterial, approveMember, deleteMessage, deleteMaterial, deleteGroup } from '../api/groupsAPI';
import { AuthContext } from '../context/AuthContext';

const DELETE_WINDOW_MS = 120 * 1000; // 2 minutes in ms

// Hook: returns seconds remaining in the 2-min delete window (null = expired)
const useDeleteCountdown = (timestamp) => {
  const getRemaining = () => {
    const elapsed = Date.now() - new Date(timestamp).getTime();
    return Math.max(0, Math.ceil((DELETE_WINDOW_MS - elapsed) / 1000));
  };
  const [remaining, setRemaining] = useState(getRemaining);

  useEffect(() => {
    if (remaining <= 0) return;
    const timer = setInterval(() => {
      const r = getRemaining();
      setRemaining(r);
      if (r <= 0) clearInterval(timer);
    }, 1000);
    return () => clearInterval(timer);
  }, [timestamp]);

  return remaining;
};

// Individual message bubble with delete
const MessageBubble = ({ msg, currentUserId, onDelete }) => {
  const isOwn = msg.sender?.id === currentUserId;
  const remaining = useDeleteCountdown(msg.timestamp);
  const canDelete = isOwn && remaining > 0;

  return (
    <div className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
      <span className="text-xs text-gray-400 mb-1">{msg.sender?.username}</span>
      <div className="flex items-end gap-2">
        {canDelete && (
          <div className="flex flex-col items-center">
            <button
              onClick={() => onDelete(msg.id)}
              title="Delete message"
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#ef4444', fontSize: '14px', padding: '2px 4px',
                borderRadius: '4px', transition: 'background 0.2s'
              }}
              onMouseEnter={e => e.target.style.background = '#fee2e2'}
              onMouseLeave={e => e.target.style.background = 'none'}
            >
              🗑️
            </button>
            <span style={{ fontSize: '9px', color: '#9ca3af' }}>{remaining}s</span>
          </div>
        )}
        <div
          className={`px-4 py-2 rounded-lg max-w-[70%] ${isOwn ? 'bg-navy-blue text-white' : 'bg-gray-100 text-gray-800'}`}
          style={{ wordBreak: 'break-word' }}
        >
          {msg.content}
          {msg.file && (
            <a
              href={msg.file}
              target="_blank"
              rel="noreferrer"
              className="block mt-1 text-xs underline opacity-80"
            >
              📎 Attachment
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

// Individual material card with delete
const MaterialCard = ({ mat, currentUserId, onDelete }) => {
  const isOwn = mat.uploaded_by?.id === currentUserId;
  const remaining = useDeleteCountdown(mat.timestamp);
  const canDelete = isOwn && remaining > 0;

  return (
    <div className="p-4 border rounded shadow-sm bg-gray-50 relative">
      {canDelete && (
        <div style={{ position: 'absolute', top: '8px', right: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ fontSize: '10px', color: '#9ca3af' }}>{remaining}s</span>
          <button
            onClick={() => onDelete(mat.id)}
            title="Delete material"
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: '16px', color: '#ef4444', padding: '2px 5px',
              borderRadius: '4px', transition: 'background 0.2s'
            }}
            onMouseEnter={e => e.target.style.background = '#fee2e2'}
            onMouseLeave={e => e.target.style.background = 'none'}
          >
            🗑️
          </button>
        </div>
      )}
      <h3 className="font-bold text-navy-blue pr-16">{mat.title}</h3>
      <p className="text-xs text-gray-500 mb-2">Uploaded by {mat.uploaded_by?.username}</p>
      <div className="flex gap-4">
        {mat.link && <a href={mat.link} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">View Link</a>}
        {mat.file && <a href={mat.file} target="_blank" rel="noreferrer" className="text-india-saffron hover:underline">Download File</a>}
      </div>
    </div>
  );
};

const GroupDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const [group, setGroup] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  // Chat state
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const chatEndRef = useRef(null);

  // Materials state
  const [materials, setMaterials] = useState([]);
  const [newMaterial, setNewMaterial] = useState({ title: '', link: '', file: null });

  useEffect(() => {
    fetchGroup();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'chat') {
      fetchMessages();
      const interval = setInterval(fetchMessages, 5000); // short-polling
      return () => clearInterval(interval);
    } else if (activeTab === 'materials') {
      fetchMaterials();
    }
  }, [activeTab, id]);

  const fetchGroup = async () => {
    try {
      const { data } = await getGroup(id);
      setGroup(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMessages = async () => {
    try {
      const { data } = await getMessages(id);
      setMessages(data);
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMaterials = async () => {
    try {
      const { data } = await getMaterials(id);
      setMaterials(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    try {
      const formData = new FormData();
      formData.append('group', id);
      formData.append('content', newMessage);
      await sendMessage(formData);
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteMessage = async (msgId) => {
    if (!window.confirm('Delete this message?')) return;
    try {
      await deleteMessage(msgId);
      setMessages(prev => prev.filter(m => m.id !== msgId));
    } catch (err) {
      const msg = err?.response?.data?.error || 'Failed to delete message.';
      alert(msg);
    }
  };

  const handleUploadMaterial = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('group', id);
      formData.append('title', newMaterial.title);
      if (newMaterial.link) formData.append('link', newMaterial.link);
      if (newMaterial.file) formData.append('file', newMaterial.file);
      await uploadMaterial(formData);
      setNewMaterial({ title: '', link: '', file: null });
      fetchMaterials();
      alert('Material uploaded!');
    } catch (err) {
      console.error(err);
      alert('Upload failed.');
    }
  };

  const handleDeleteMaterial = async (matId) => {
    if (!window.confirm('Delete this material?')) return;
    try {
      await deleteMaterial(matId);
      setMaterials(prev => prev.filter(m => m.id !== matId));
    } catch (err) {
      const msg = err?.response?.data?.error || 'Failed to delete material.';
      alert(msg);
    }
  };

  const handleApprove = async (userId) => {
    try {
      await approveMember(id, userId);
      fetchGroup();
    } catch (err) {
      alert('Failed to approve member.');
    }
  };

  const handleDeleteGroup = async () => {
    if (!window.confirm('Are you sure you want to delete this group? This action cannot be undone.')) return;
    try {
      await deleteGroup(id);
      navigate('/groups');
    } catch (err) {
      const msg = err?.response?.data?.error || 'Failed to delete group.';
      alert(msg);
    }
  };

  if (!group) return <div className="pt-24 text-center">Loading...</div>;

  const isAdmin = group.members.some(m => m.user?.id === user?.id && m.role === 'Admin');

  return (
    <div className="pt-24 pb-12 max-w-5xl mx-auto px-4">
      <div className="bg-white rounded-t-lg shadow p-6 mb-1 border-b-4 border-india-saffron">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-navy-blue">{group.name}</h1>
            <p className="text-gray-600 mt-2">{group.description}</p>
          </div>
          {isAdmin && (
            <button
              onClick={handleDeleteGroup}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition duration-200"
            >
              Delete Group
            </button>
          )}
        </div>
        <div className="mt-4 flex gap-4 border-b">
          <button
            className={`pb-2 px-4 font-bold ${activeTab === 'chat' ? 'border-b-2 border-navy-blue text-navy-blue' : 'text-gray-500'}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button
            className={`pb-2 px-4 font-bold ${activeTab === 'materials' ? 'border-b-2 border-navy-blue text-navy-blue' : 'text-gray-500'}`}
            onClick={() => setActiveTab('materials')}
          >
            Materials
          </button>
          {isAdmin && (
            <button
              className={`pb-2 px-4 font-bold ${activeTab === 'members' ? 'border-b-2 border-navy-blue text-navy-blue' : 'text-gray-500'}`}
              onClick={() => setActiveTab('members')}
            >
              Members Requests
            </button>
          )}
        </div>
      </div>

      <div className="bg-white shadow rounded-b-lg p-6 min-h-[500px] flex flex-col">
        {activeTab === 'chat' && (
          <>
            <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2" style={{ maxHeight: '420px' }}>
              {messages.map(msg => (
                <MessageBubble
                  key={msg.id}
                  msg={msg}
                  currentUserId={user?.id}
                  onDelete={handleDeleteMessage}
                />
              ))}
              <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className="flex gap-2 mt-auto">
              <input
                type="text"
                value={newMessage}
                onChange={e => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 border p-2 rounded focus:outline-navy-blue"
              />
              <button type="submit" className="bg-india-saffron text-white px-6 rounded font-bold hover:bg-opacity-90">Send</button>
            </form>
          </>
        )}

        {activeTab === 'materials' && (
          <div className="flex gap-8 flex-col md:flex-row">
            <div className="flex-1">
              <h2 className="text-xl font-bold mb-4">Study Materials</h2>
              <div className="space-y-4">
                {materials.map(mat => (
                  <MaterialCard
                    key={mat.id}
                    mat={mat}
                    currentUserId={user?.id}
                    onDelete={handleDeleteMaterial}
                  />
                ))}
                {materials.length === 0 && <p className="text-gray-500">No materials uploaded yet.</p>}
              </div>
            </div>
            <div className="w-full md:w-1/3 bg-gray-50 p-4 rounded border">
              <h2 className="text-lg font-bold mb-4">Upload Material</h2>
              <form onSubmit={handleUploadMaterial} className="space-y-4">
                <input type="text" placeholder="Title" required value={newMaterial.title} onChange={e => setNewMaterial({...newMaterial, title: e.target.value})} className="w-full border p-2 rounded" />
                <input type="url" placeholder="Resource Link (Optional)" value={newMaterial.link} onChange={e => setNewMaterial({...newMaterial, link: e.target.value})} className="w-full border p-2 rounded" />
                <div>
                  <label className="block text-sm text-gray-600 mb-1">File (Optional)</label>
                  <input type="file" onChange={e => setNewMaterial({...newMaterial, file: e.target.files[0]})} className="w-full text-sm" />
                </div>
                <button type="submit" className="w-full bg-navy-blue text-white py-2 rounded">Upload</button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'members' && isAdmin && (
          <div>
            <h2 className="text-xl font-bold mb-4">Pending Requests</h2>
            <div className="space-y-4">
              {group.members.filter(m => !m.is_approved).map(m => (
                <div key={m.id} className="flex justify-between items-center p-4 border rounded">
                  <span>{m.user?.username} ({m.user?.first_name} {m.user?.last_name})</span>
                  <button onClick={() => handleApprove(m.user?.id)} className="bg-green-500 text-white px-4 py-1 rounded">Approve</button>
                </div>
              ))}
              {group.members.filter(m => !m.is_approved).length === 0 && (
                <p className="text-gray-500">No pending requests.</p>
              )}
            </div>

            <h2 className="text-xl font-bold mt-8 mb-4">Approved Members</h2>
            <div className="space-y-2">
              {group.members.filter(m => m.is_approved).map(m => (
                <div key={m.id} className="p-2 border-b flex justify-between">
                  <span>{m.user?.username}</span>
                  <span className="text-sm bg-gray-200 px-2 rounded-full">{m.role}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupDetail;
