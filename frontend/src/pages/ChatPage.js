// frontend/src/pages/ChatPage.js
import React, { useState, useEffect, useContext, useCallback, useRef } from 'react';
import axios from 'axios';
import { AuthContext } from '../contexts/AuthContext';
import { UserProfileContext } from '../contexts/UserProfileContext';
import { Layout, List, Avatar, Input, Button, Spin, Alert, Typography, Space } from 'antd'; // 移除了 Menu, Card, Popover
import { SendOutlined, UserOutlined, TeamOutlined, LogoutOutlined, ArrowLeftOutlined } from '@ant-design/icons'; // 移除了 EllipsisOutlined
import './ChatPage.css';
import { Link } from 'react-router-dom';


const { Header, Sider, Content, Footer } = Layout;
const { Text, Title } = Typography;
const { Search } = Input; // Search 是从 Input 中解构出来的

// --- 子组件：联系人列表项 (AntD List.Item) ---
const ContactItem = ({ contact, isSelected, onSelectContact }) => {
    const defaultAvatarIcon = contact.type === 'group' 
        ? <TeamOutlined /> 
        : <UserOutlined />;
    return (
        <List.Item
            onClick={() => onSelectContact(contact)}
            className={`contact-item ${isSelected ? 'selected' : ''}`}
            style={{ padding: '12px 16px', cursor: 'pointer' }}
        >
            <List.Item.Meta
                avatar={<Avatar src={contact.avatar_url} icon={!contact.avatar_url && defaultAvatarIcon} size="large" />}
                title={<Text strong ellipsis className="contact-name">{contact.name}</Text>}
                description={
                    <Text type="secondary" ellipsis className="contact-last-message">
                        {contact.last_message || (contact.type === 'group' ? 'Group chat' : 'Friend chat')}
                    </Text>
                }
            />
            {contact.last_message_time && <Text type="secondary" style={{ fontSize: '0.75rem' }}>{contact.last_message_time}</Text>}
        </List.Item>
    );
};

// --- 子组件：消息项 ---
const MessageItem = ({ message, currentUser }) => {
    const isSelf = message.sender_id === currentUser?.user_id;
    // 假设后端返回的是 '%Y-%m-%d %H:%M:%S' 格式的时间
    // TODO: 日期表示有问题 ！
    const sentAtDate = message.sent_at ? new Date(message.sent_at) : new Date();
    const formattedTime = sentAtDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const defaultAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(message.sender_nickname || 'U')}&background=random&color=fff&rounded=true&size=32`;
    const currentUserAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser?.nickname || currentUser?.username || 'M')}&background=4CAF50&color=fff&rounded=true&size=32`;


    return (
        <div className={`message-item-wrapper ${isSelf ? 'self' : 'other'}`}>
            {!isSelf && (
                <Avatar 
                    src={message.sender_avatar_url || defaultAvatar} 
                    icon={!message.sender_avatar_url && <UserOutlined />}
                    size="small" 
                    className="message-avatar"
                />
            )}
            <div className={`message-bubble ${isSelf ? 'self-bubble' : 'other-bubble'}`}>
                {!isSelf && message.sender_nickname && (
                     <Text strong className="message-sender-name">{message.sender_nickname}</Text>
                )}
                <Text className="message-content">{message.content}</Text>
                <Text type="secondary" className="message-time">{formattedTime}</Text>
            </div>
            {isSelf && (
                 <Avatar 
                    src={currentUser?.avatar_url || currentUserAvatar} 
                    icon={!currentUser?.avatar_url && <UserOutlined />}
                    size="small" 
                    className="message-avatar"
                />
            )}
        </div>
    );
};

// --- 子组件：消息区域 (这里是补充的定义) ---
const MessagesArea = ({ messages, currentUser, isLoading, error }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    if (isLoading) return <div className="flex-1 p-6 text-center text-gray-500"><Spin tip="Loading messages..." /></div>;
    if (error) return <div className="flex-1 p-6 text-center text-red-500"><Alert message="Error" description={error} type="error" showIcon /></div>;
    if (!messages || messages.length === 0) {
        return <div className="flex-1 p-6 flex items-center justify-center text-gray-400 italic">No messages in this chat yet.</div>;
    }

    return (
        <div className="messages-area-content"> {/* 使用 ChatPage.css 中定义的样式 */}
            {messages.map(message => (
                <MessageItem key={message.id || `msg-${Math.random()}`} message={message} currentUser={currentUser} />
            ))}
            <div ref={messagesEndRef} />
        </div>
    );
};


// --- 子组件：消息输入框 ---
const MessageInput = ({ onSendMessage, disabled }) => {
    // ... (保持不变)
    const [messageContent, setMessageContent] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (messageContent.trim() && !disabled) {
            onSendMessage(messageContent.trim());
            setMessageContent('');
        }
    };

    return (
        <Input.Search
            placeholder="Type a message..."
            enterButton={<Button type="primary" icon={<SendOutlined />} disabled={disabled}>Send</Button>}
            value={messageContent}
            onChange={(e) => setMessageContent(e.target.value)}
            //onSearch={handleSendMessage} // onSearch 对应点击发送按钮或回车
            disabled={disabled}
            size="large"
            className="message-input-search" // 添加class以便在CSS中调整
        />
    );
};

// --- 子组件：聊天窗口头部 ---
const ChatHeader = ({ contact, onBack, isMobileView }) => { // 添加 onBack 和 isMobileView
    if (!contact) return null;
    const defaultAvatarIcon = contact.type === 'group' ? <TeamOutlined /> : <UserOutlined />;

    return (
        <Header className="chat-header">
            {isMobileView && ( // 只有在移动视图且有返回操作时显示
                <Button 
                    icon={<ArrowLeftOutlined />} 
                    type="text" 
                    onClick={onBack}
                    style={{ marginRight: 16, color: '#595959' }} // 调整颜色以适应白色背景
                />
            )}
            <Avatar src={contact.avatar_url} icon={!contact.avatar_url && defaultAvatarIcon} />
            <Title level={5} style={{ marginLeft: 12, marginBottom: 0, flexGrow: 1 }} ellipsis>
                {contact.name}
            </Title>
            {/* <Popover content={<div>More actions...</div>} trigger="click">
                <Button type="text" icon={<EllipsisOutlined style={{fontSize: '20px', color: '#595959'}} />} />
            </Popover> 
            */}
        </Header>
    );
};


// --- 主聊天页面组件 ---
function ChatPage() {
    const { logout } = useContext(AuthContext);
    const { profile: currentUser, isLoadingProfile, profileError } = useContext(UserProfileContext);

    const [contacts, setContacts] = useState([]);
    const [selectedContact, setSelectedContact] = useState(null);
    const [messages, setMessages] = useState([]);
    const [collapsedSider, setCollapsedSider] = useState(false); // Sider 收起状态
    const [isMobileView, setIsMobileView] = useState(window.innerWidth < 768);
    
    // 在移动端，当选择了联系人后，我们应该只显示聊天窗口，隐藏联系人列表
    // 当从聊天窗口返回时，显示联系人列表，隐藏聊天窗口
    const [showChatPaneOnMobile, setShowChatPaneOnMobile] = useState(false);


    const [isLoadingContacts, setIsLoadingContacts] = useState(true);
    const [isLoadingMessages, setIsLoadingMessages] = useState(false);
    const [errorContacts, setErrorContacts] = useState(null);
    const [errorMessages, setErrorMessages] = useState(null);
    // messageInput 状态移到 MessageInput 组件内部，或者在这里管理并通过 props 传递给 MessageInput

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    useEffect(() => {
        const handleResize = () => {
            const mobile = window.innerWidth < 768;
            setIsMobileView(mobile);
            if (mobile && selectedContact) {
                setShowChatPaneOnMobile(true); // 如果是移动端且有选中的联系人，则显示聊天窗格
            } else if (!mobile) {
                setShowChatPaneOnMobile(false); // 桌面端总是显示两个窗格（如果 sider 没折叠）
            }
        };
        window.addEventListener('resize', handleResize);
        handleResize(); 
        return () => window.removeEventListener('resize', handleResize);
    }, [selectedContact]);


    const fetchContacts = useCallback(async () => {
        if (!currentUser) return; 
        setIsLoadingContacts(true);
        setErrorContacts(null);
        try {
            const response = await axios.get(`${API_BASE_URL}/api/chat/contacts`);
            setContacts(response.data.contacts || []);
        } catch (err) {
            setErrorContacts(err.response?.data?.error || 'Could not load contacts.');
        } finally {
            setIsLoadingContacts(false);
        }
    }, [currentUser, API_BASE_URL]); // 移除了 selectedContact

    useEffect(() => {
        fetchContacts();
    }, [fetchContacts]); 


    const fetchMessages = useCallback(async (contact) => {
        if (!contact) return;
        setIsLoadingMessages(true);
        setErrorMessages(null);
        setMessages([]); 
        try {
            const response = await axios.get(`${API_BASE_URL}/api/chat/messages/${contact.type}/${contact.contact_id}`);
            setMessages(response.data.messages || []);
        } catch (err) {
            setErrorMessages(err.response?.data?.error || 'Could not load messages.');
        } finally {
            setIsLoadingMessages(false);
        }
    }, [API_BASE_URL]);

    const handleSelectContact = useCallback((contact) => {
        if (selectedContact && selectedContact.type === contact.type && selectedContact.contact_id === contact.contact_id) {
            if (isMobileView) setShowChatPaneOnMobile(true); // 如果点击已选中的，在移动端也确保显示聊天
            return; 
        }
        setSelectedContact(contact);
        fetchMessages(contact); 
        if (isMobileView) {
            setShowChatPaneOnMobile(true); 
        }
        // TODO: socket.emit('join_chat', ...);
    }, [fetchMessages, selectedContact, isMobileView]);

    const handleSendMessage = (messageContent) => { // messageContent 由 MessageInput 组件传入
        if (!messageContent.trim() || !selectedContact || !currentUser) return;
        
        // TODO: 使用 SocketIO 发送消息
        // socket.emit('send_message', { message_content: messageContent, contact_id: selectedContact.contact_id, contact_type: selectedContact.type });

        const optimisticMessage = {
            id: `temp-${Date.now()}`,
            sender_id: currentUser.user_id,
            // sender_nickname: currentUser.nickname || currentUser.username, // MessageItem 会处理
            // sender_avatar_url: currentUser.avatar_url,                   // MessageItem 会处理
            content: messageContent.trim(),
            sent_at: new Date().toISOString(), 
            is_self: true,
        };
        setMessages(prev => [...prev, optimisticMessage]);
    };
    
    const handleBackToContacts = () => {
        setSelectedContact(null);
        setShowChatPaneOnMobile(false);
    };
    
    if (isLoadingProfile) return <div className="loading-screen"><Spin size="large" tip="Loading Profile..." /></div>;
    if (profileError) return <div className="error-screen"><Alert message="Profile Error" description={profileError.msg || "Could not load user profile."} type="error" showIcon /></div>;
    if (!currentUser) return <div className="loading-screen"><Alert message="Authentication Error" description="User not authenticated." type="error" showIcon /></div>;

    const siderContent = (
        <>
            <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                <Search placeholder="Search contacts" onSearch={(value) => console.log(value)} />
            </div>
            {isLoadingContacts ? (
                <div style={{textAlign: 'center', padding: '20px'}}><Spin /></div>
            ) : errorContacts ? (
                <Alert message="Error" description={errorContacts} type="error" showIcon style={{margin: '16px'}}/>
            ) : (
                <List
                    itemLayout="horizontal"
                    dataSource={contacts}
                    className="contact-list-scrollable" // 用于自定义滚动条
                    renderItem={(contact) => (
                        <ContactItem
                            contact={contact}
                            isSelected={selectedContact?.contact_id === contact.contact_id && selectedContact?.type === contact.type}
                            onSelectContact={handleSelectContact}
                        />
                    )}
                />
            )}
        </>
    );

    const chatWindowContent = (
        selectedContact ? (
            <Layout className="chat-window-layout"> {/* 使用 class 以便 CSS 控制 */}
                <ChatHeader contact={selectedContact} onBack={handleBackToContacts} isMobileView={isMobileView && showChatPaneOnMobile} />
                <Content className="messages-area-container"> {/* 这个 Content 就是之前的 MessagesArea */}
                    <MessagesArea messages={messages} currentUser={currentUser} isLoading={isLoadingMessages} error={errorMessages} />
                </Content>
                <Footer className="message-input-footer">
                    <MessageInput onSendMessage={handleSendMessage} disabled={isLoadingMessages || !selectedContact} />
                </Footer>
            </Layout>
        ) : (
            <div className="no-chat-selected">
                <TeamOutlined style={{ fontSize: '64px', color: '#bfbfbf' }}/>
                <Text type="secondary" style={{ marginTop: 16, fontSize: '18px' }}>Select a chat to start messaging</Text>
            </div>
        )
    );


    return (
        <Layout style={{ minHeight: '100vh' }} className="chat-page-layout">
            <Header className="app-header">
                <div className="logo">KaguChat</div>
                <div>
                <Link to="/admin" style={{ marginRight: '1rem', padding: '0.5rem 1rem', background: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
                        Admin Panel
                </Link>
                <Space>
                    <Avatar src={currentUser.avatar_url} icon={!currentUser.avatar_url && <UserOutlined />} />
                    <Text style={{ color: 'white' }}>{currentUser.nickname || currentUser.username}</Text>
                    <Button type="primary" danger icon={<LogoutOutlined />} onClick={logout}>
                        Logout
                    </Button>
                </Space>
                </div>
            </Header>
            <Layout className="main-chat-layout">
                {isMobileView ? (
                    // 在移动端，根据 showChatPaneOnMobile 决定显示哪个面板
                    showChatPaneOnMobile ? chatWindowContent : <Sider width="100%" theme="light" className="contact-sider-mobile">{siderContent}</Sider>
                ) : (
                    // 桌面端同时显示 Sider 和 Content
                    <>
                        <Sider
                            width={320} // 可以适当调整宽度
                            theme="light"
                            collapsible
                            collapsed={collapsedSider}
                            onCollapse={(value) => setCollapsedSider(value)}
                            className="contact-sider"
                        >
                           {!collapsedSider && siderContent}
                        </Sider>
                        <Content className="chat-content-area">
                           {chatWindowContent}
                        </Content>
                    </>
                )}
            </Layout>
        </Layout>
    );
}

export default ChatPage;