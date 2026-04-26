import api from './axiosConfig';

export const getNotifications = async () => {
    try {
        const response = await api.get('/users/notifications/');
        return response.data;
    } catch (error) {
        throw error.response?.data || { error: 'Failed to fetch notifications' };
    }
};

export const markNotificationRead = async (id) => {
    try {
        const response = await api.post(`/users/notifications/${id}/read/`);
        return response.data;
    } catch (error) {
        throw error.response?.data || { error: 'Failed to mark as read' };
    }
};
