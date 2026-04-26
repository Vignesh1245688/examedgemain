import api from './axiosConfig';

export const getGroups = (params) => {
  return api.get('groups/groups/', { params });
};

export const getGroup = (id) => {
  return api.get(`groups/groups/${id}/`);
};

export const deleteGroup = (id) => {
  return api.delete(`groups/groups/${id}/`);
};

export const requestJoinGroup = (id) => {
  return api.post(`groups/groups/${id}/request_join/`);
};

export const approveMember = (groupId, userId) => {
  return api.post(`groups/groups/${groupId}/approve_member/`, { user_id: userId });
};

export const createGroup = (data) => {
  return api.post('groups/groups/', data);
};

export const getMessages = (groupId) => {
  return api.get('groups/messages/', { params: { group_id: groupId } });
};

export const sendMessage = (data) => {
  // data should be FormData if there's a file
  return api.post('groups/messages/', data);
};

export const getMaterials = (groupId) => {
  return api.get('groups/materials/', { params: { group_id: groupId } });
};

export const uploadMaterial = (data) => {
  return api.post('groups/materials/', data);
};

export const deleteMessage = (messageId) => {
  return api.delete(`groups/messages/${messageId}/`);
};

export const deleteMaterial = (materialId) => {
  return api.delete(`groups/materials/${materialId}/`);
};
