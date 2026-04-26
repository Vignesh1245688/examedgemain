import { useState, useEffect, useContext } from 'react';
import { getGroups, requestJoinGroup, createGroup } from '../api/groupsAPI';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Groups = () => {
  const [groups, setGroups] = useState([]);
  const [examType, setExamType] = useState('');
  const [examName, setExamName] = useState('');
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Create group form state
  const [showCreate, setShowCreate] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', description: '', exam_type: 'Central', exam_name: '' });

  useEffect(() => {
    fetchGroups();
  }, [examType, examName]);

  const fetchGroups = async () => {
    try {
      const { data } = await getGroups({ exam_type: examType, exam_name: examName });
      setGroups(data);
    } catch (err) {
      console.error('Failed to fetch groups', err);
    }
  };

  const handleJoin = async (groupId) => {
    try {
      await requestJoinGroup(groupId);
      alert('Join request sent!');
      fetchGroups(); // refresh groups to possibly show membership status if updated
    } catch (err) {
      alert('Failed to request join.');
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createGroup(newGroup);
      alert('Group created successfully!');
      setShowCreate(false);
      fetchGroups();
    } catch (err) {
      alert('Failed to create group.');
    }
  };

  return (
    <div className="pt-24 pb-12 max-w-7xl mx-auto px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Study Groups</h1>
        <button 
          onClick={() => setShowCreate(!showCreate)}
          className="bg-navy-blue text-white px-4 py-2 rounded shadow hover:bg-opacity-90 transition"
        >
          {showCreate ? 'Cancel Create' : '+ Create Group'}
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white p-6 rounded shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Create New Group</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" placeholder="Group Name" required value={newGroup.name} onChange={e => setNewGroup({...newGroup, name: e.target.value})} className="border p-2 rounded" />
            <select value={newGroup.exam_type} onChange={e => setNewGroup({...newGroup, exam_type: e.target.value})} className="border p-2 rounded">
              <option value="Central">Central</option>
              <option value="State">State</option>
            </select>
            <input type="text" placeholder="Exam Name (e.g. UPSC)" required value={newGroup.exam_name} onChange={e => setNewGroup({...newGroup, exam_name: e.target.value})} className="border p-2 rounded" />
            <input type="text" placeholder="Description" required value={newGroup.description} onChange={e => setNewGroup({...newGroup, description: e.target.value})} className="border p-2 rounded" />
          </div>
          <button type="submit" className="mt-4 bg-india-saffron text-white px-6 py-2 rounded shadow hover:bg-opacity-90">Create</button>
        </form>
      )}

      <div className="flex gap-4 mb-8">
        <input 
          type="text" 
          placeholder="Search by Exam Name..." 
          value={examName} 
          onChange={(e) => setExamName(e.target.value)}
          className="border p-2 rounded w-full md:w-1/3"
        />
        <select 
          value={examType} 
          onChange={(e) => setExamType(e.target.value)}
          className="border p-2 rounded w-full md:w-1/4"
        >
          <option value="">All Exam Types</option>
          <option value="Central">Central</option>
          <option value="State">State</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {groups.map(group => {
          // Check if user is already a member
          const membership = group.members.find(m => m.user?.id === user?.id || (m.user && m.user.username === user?.username));
          
          return (
            <div key={group.id} className="bg-white p-6 rounded shadow flex flex-col justify-between border-t-4 border-navy-blue">
              <div>
                <h2 className="text-xl font-bold mb-2 text-navy-blue">{group.name}</h2>
                <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                  <span className="bg-gray-100 px-2 py-1 rounded">{group.exam_type}</span>
                  <span className="font-semibold text-india-saffron">{group.exam_name}</span>
                </div>
                <p className="text-gray-700 mb-4 line-clamp-3">{group.description}</p>
                <div className="flex items-center text-sm text-gray-500 font-medium mb-4">
                  <span className="bg-blue-100 text-blue-800 py-1 px-2 rounded-full text-xs">{group.members.filter(m => m.is_approved).length} Approved Members</span>
                </div>
              </div>
              
              {!membership ? (
                <button 
                  onClick={() => handleJoin(group.id)}
                  className="w-full bg-india-saffron text-white py-2 rounded hover:bg-opacity-90 transition font-bold"
                >
                  Join Group
                </button>
              ) : membership.is_approved ? (
                <button 
                  onClick={() => navigate(`/groups/${group.id}`)}
                  className="w-full bg-navy-blue text-white py-2 rounded hover:bg-opacity-90 transition font-bold"
                >
                  Enter Group
                </button>
              ) : (
                <button 
                  disabled
                  className="w-full bg-gray-200 text-gray-500 py-2 rounded font-bold cursor-not-allowed"
                >
                  Request Pending
                </button>
              )}
            </div>
          );
        })}
        {groups.length === 0 && (
          <div className="col-span-3 text-center text-gray-500 py-12">
            No groups found. Be the first to create one!
          </div>
        )}
      </div>
    </div>
  );
};

export default Groups;
