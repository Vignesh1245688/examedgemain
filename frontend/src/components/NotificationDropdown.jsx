import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check, Users, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getNotifications, markNotificationRead } from '../api/notificationsAPI';

const NotificationDropdown = () => {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  const fetchNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkRead = async (id, e) => {
    e.stopPropagation();
    try {
      await markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((notif) =>
          notif.id === id ? { ...notif, is_read: true } : notif
        )
      );
    } catch (error) {
      console.error('Failed to mark as read', error);
    }
  };

  const handleNotifClick = async (notif) => {
    // Mark as read when clicked
    if (!notif.is_read) {
      try {
        await markNotificationRead(notif.id);
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === notif.id ? { ...n, is_read: true } : n
          )
        );
      } catch (error) {
        console.error('Failed to mark as read', error);
      }
    }
    // Navigate to the group if group_id exists
    if (notif.group_id) {
      setIsOpen(false);
      navigate(`/groups/${notif.group_id}`);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  // Determine notification icon based on message content
  const getNotifIcon = (msg) => {
    if (msg.includes('approved')) {
      return <Users className="w-5 h-5 text-green-500 shrink-0" />;
    }
    return <MessageCircle className="w-5 h-5 text-blue-500 shrink-0" />;
  };

  // Extract group name from message
  const getGroupName = (msg) => {
    const match = msg.match(/'([^']+)'/);
    return match ? match[1] : null;
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-navy-blue transition-colors focus:outline-none"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-100 z-50 overflow-hidden">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-navy-blue to-blue-700 flex justify-between items-center">
            <h3 className="font-bold text-white text-lg">Notifications</h3>
            {unreadCount > 0 && (
              <span className="text-xs bg-white/20 text-white px-3 py-1 rounded-full font-medium">
                {unreadCount} New
              </span>
            )}
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto divide-y divide-gray-50">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-400">
                <Bell className="w-10 h-10 mx-auto mb-3 text-gray-300" />
                <p className="text-sm font-medium">No notifications yet</p>
                <p className="text-xs mt-1">You'll see group alerts here</p>
              </div>
            ) : (
              notifications.map((notif) => {
                const groupName = getGroupName(notif.message);
                return (
                  <div
                    key={notif.id}
                    onClick={() => handleNotifClick(notif)}
                    className={`p-4 flex items-start gap-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                      !notif.is_read ? 'bg-blue-50/60 border-l-4 border-l-navy-blue' : 'border-l-4 border-l-transparent'
                    }`}
                  >
                    {/* Icon */}
                    <div className="mt-0.5">
                      {getNotifIcon(notif.message)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm leading-snug ${!notif.is_read ? 'text-gray-900 font-medium' : 'text-gray-600'}`}>
                        {notif.message}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5">
                        {groupName && (
                          <span className="text-xs bg-navy-blue/10 text-navy-blue px-2 py-0.5 rounded-full font-medium">
                            📌 {groupName}
                          </span>
                        )}
                        {notif.group_id && (
                          <span className="text-xs text-blue-500 hover:underline">
                            View Group →
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Mark as read button */}
                    {!notif.is_read && (
                      <button
                        onClick={(e) => handleMarkRead(notif.id, e)}
                        className="p-1.5 text-blue-500 hover:bg-blue-100 rounded-full transition-colors shrink-0"
                        title="Mark as read"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
