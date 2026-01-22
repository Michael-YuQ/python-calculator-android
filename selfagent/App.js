import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Modal,
  TextInput,
  Alert,
  StatusBar,
  Animated,
  Dimensions,
  Platform,
} from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView, SafeAreaProvider } from 'react-native-safe-area-context';

const { width, height } = Dimensions.get('window');

// 配置通知处理
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

const API_BASE = 'http://111.170.6.103:9999';
const SCHEDULE_API = `${API_BASE}/api/daily.php`;
const WS_URL = 'ws://111.170.6.103:9999/ws';  // WebSocket 地址

function MainApp() {
  const [sites, setSites] = useState([
    { id: '1', name: '主系统', url: 'http://111.170.6.103:9999/' }
  ]);
  const [currentSite, setCurrentSite] = useState(null);
  const [showSiteList, setShowSiteList] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [newSiteName, setNewSiteName] = useState('');
  const [newSiteUrl, setNewSiteUrl] = useState('');
  const [schedules, setSchedules] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  
  const notificationListener = useRef();
  const responseListener = useRef();
  const slideAnim = useRef(new Animated.Value(-300)).current;
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  // WebSocket 连接管理
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    console.log('正在连接 WebSocket...');
    wsRef.current = new WebSocket(WS_URL);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket 已连接');
      setWsConnected(true);
      // 清除重连定时器
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };
    
    wsRef.current.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到消息:', data);
        
        // 弹出系统通知
        await Notifications.scheduleNotificationAsync({
          content: {
            title: data.title || '📢 新消息',
            body: data.message || data.body || event.data,
            data: data,
          },
          trigger: null, // 立即显示
        });
        
        // 添加到通知列表
        setNotifications(prev => [
          { 
            id: Date.now().toString(), 
            title: data.title || '📢 新消息',
            body: data.message || data.body || event.data,
          },
          ...prev
        ]);
      } catch (e) {
        // 如果不是 JSON，直接显示文本
        await Notifications.scheduleNotificationAsync({
          content: {
            title: '📢 新消息',
            body: event.data,
          },
          trigger: null,
        });
        setNotifications(prev => [
          { id: Date.now().toString(), title: '📢 新消息', body: event.data },
          ...prev
        ]);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.log('WebSocket 错误:', error);
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket 已断开，5秒后重连...');
      setWsConnected(false);
      // 5秒后自动重连
      reconnectTimer.current = setTimeout(connectWebSocket, 5000);
    };
  };

  useEffect(() => {
    loadSites();
    loadSchedules();
    registerForPushNotifications();
    setupDailyReminder();
    connectWebSocket();  // 启动 WebSocket 连接

    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      setNotifications(prev => [
        { id: Date.now().toString(), ...notification.request.content },
        ...prev
      ]);
    });

    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      console.log(response);
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener.current);
      Notifications.removeNotificationSubscription(responseListener.current);
      // 清理 WebSocket
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
    };
  }, []);

  useEffect(() => {
    Animated.timing(slideAnim, {
      toValue: showNotifications ? 0 : -300,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [showNotifications]);

  const registerForPushNotifications = async () => {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') {
      Alert.alert('提示', '需要通知权限才能接收日程提醒');
    }
  };

  const loadSites = async () => {
    try {
      const saved = await AsyncStorage.getItem('sites');
      if (saved) setSites(JSON.parse(saved));
    } catch (e) {
      console.error('加载站点失败:', e);
    }
  };

  const saveSites = async (newSites) => {
    try {
      await AsyncStorage.setItem('sites', JSON.stringify(newSites));
      setSites(newSites);
    } catch (e) {
      console.error('保存站点失败:', e);
    }
  };

  const loadSchedules = async () => {
    try {
      const response = await fetch(SCHEDULE_API);
      const data = await response.json();
      if (Array.isArray(data)) {
        setSchedules(data);
        scheduleNotifications(data);
      }
    } catch (e) {
      console.error('加载日程失败:', e);
    }
  };


  const setupDailyReminder = async () => {
    // 每天早上8点提醒
    await Notifications.cancelAllScheduledNotificationsAsync();
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '📅 今日日程',
        body: '点击查看今天的安排',
        data: { type: 'daily' },
      },
      trigger: {
        hour: 8,
        minute: 0,
        repeats: true,
      },
    });
  };

  const scheduleNotifications = async (scheduleList) => {
    for (const item of scheduleList) {
      if (item.time) {
        const [hours, minutes] = item.time.split(':').map(Number);
        const now = new Date();
        const scheduleTime = new Date();
        scheduleTime.setHours(hours, minutes, 0, 0);
        
        // 提前15分钟提醒
        const reminderTime = new Date(scheduleTime.getTime() - 15 * 60 * 1000);
        
        if (reminderTime > now) {
          await Notifications.scheduleNotificationAsync({
            content: {
              title: '⏰ 日程提醒',
              body: `${item.title || item.content} 将在15分钟后开始`,
              data: { scheduleId: item.id },
            },
            trigger: reminderTime,
          });
        }
      }
    }
  };

  const addSite = () => {
    if (!newSiteName.trim() || !newSiteUrl.trim()) {
      Alert.alert('提示', '请填写完整信息');
      return;
    }
    let url = newSiteUrl.trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    const newSite = {
      id: Date.now().toString(),
      name: newSiteName.trim(),
      url: url,
    };
    saveSites([...sites, newSite]);
    setNewSiteName('');
    setNewSiteUrl('');
    setShowAddModal(false);
  };

  const deleteSite = (id) => {
    Alert.alert('确认删除', '确定要删除这个站点吗？', [
      { text: '取消', style: 'cancel' },
      { text: '删除', style: 'destructive', onPress: () => {
        saveSites(sites.filter(s => s.id !== id));
      }},
    ]);
  };

  const renderSiteItem = ({ item }) => (
    <TouchableOpacity
      style={styles.siteCard}
      onPress={() => {
        setCurrentSite(item);
        setShowSiteList(false);
      }}
      onLongPress={() => deleteSite(item.id)}
    >
      <View style={styles.siteIcon}>
        <Ionicons name="globe-outline" size={28} color="#667eea" />
      </View>
      <View style={styles.siteInfo}>
        <Text style={styles.siteName}>{item.name}</Text>
        <Text style={styles.siteUrl} numberOfLines={1}>{item.url}</Text>
      </View>
      <Ionicons name="chevron-forward" size={24} color="#ccc" />
    </TouchableOpacity>
  );

  const renderScheduleItem = ({ item }) => (
    <View style={styles.scheduleItem}>
      <View style={styles.scheduleTime}>
        <Text style={styles.scheduleTimeText}>{item.time || '--:--'}</Text>
      </View>
      <View style={styles.scheduleContent}>
        <Text style={styles.scheduleTitle}>{item.title || item.content}</Text>
        {item.description && (
          <Text style={styles.scheduleDesc}>{item.description}</Text>
        )}
      </View>
    </View>
  );

  const renderNotificationItem = ({ item }) => (
    <View style={styles.notificationItem}>
      <Text style={styles.notificationTitle}>{item.title}</Text>
      <Text style={styles.notificationBody}>{item.body}</Text>
    </View>
  );


  // 主页面 - 站点列表
  if (showSiteList) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#667eea" />
        
        {/* 顶部导航栏 */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>SelfAgent</Text>
          <View style={styles.headerRight}>
            <TouchableOpacity
              style={styles.headerBtn}
              onPress={() => setShowScheduleModal(true)}
            >
              <Ionicons name="calendar-outline" size={24} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.headerBtn}
              onPress={() => setShowNotifications(!showNotifications)}
            >
              <Ionicons name="notifications-outline" size={24} color="#fff" />
              {notifications.length > 0 && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>{notifications.length}</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* 通知下拉面板 */}
        <Animated.View style={[styles.notificationPanel, { transform: [{ translateY: slideAnim }] }]}>
          <View style={styles.notificationHeader}>
            <Text style={styles.notificationHeaderText}>消息通知</Text>
            <TouchableOpacity onPress={() => setNotifications([])}>
              <Text style={styles.clearBtn}>清空</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={notifications}
            renderItem={renderNotificationItem}
            keyExtractor={item => item.id}
            ListEmptyComponent={
              <Text style={styles.emptyText}>暂无通知</Text>
            }
          />
        </Animated.View>

        {/* 站点列表 */}
        <FlatList
          data={sites}
          renderItem={renderSiteItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.siteList}
          ListHeaderComponent={
            <Text style={styles.sectionTitle}>我的站点</Text>
          }
          ListFooterComponent={
            <TouchableOpacity
              style={styles.addCard}
              onPress={() => setShowAddModal(true)}
            >
              <Ionicons name="add-circle-outline" size={40} color="#667eea" />
              <Text style={styles.addText}>添加新站点</Text>
            </TouchableOpacity>
          }
        />

        {/* 添加站点弹窗 */}
        <Modal visible={showAddModal} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>添加站点</Text>
              <TextInput
                style={styles.input}
                placeholder="站点名称"
                value={newSiteName}
                onChangeText={setNewSiteName}
                placeholderTextColor="#999"
              />
              <TextInput
                style={styles.input}
                placeholder="站点地址 (http://...)"
                value={newSiteUrl}
                onChangeText={setNewSiteUrl}
                autoCapitalize="none"
                keyboardType="url"
                placeholderTextColor="#999"
              />
              <View style={styles.modalBtns}>
                <TouchableOpacity
                  style={[styles.modalBtn, styles.cancelBtn]}
                  onPress={() => setShowAddModal(false)}
                >
                  <Text style={styles.cancelBtnText}>取消</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalBtn, styles.confirmBtn]}
                  onPress={addSite}
                >
                  <Text style={styles.confirmBtnText}>添加</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* 日程弹窗 */}
        <Modal visible={showScheduleModal} transparent animationType="slide">
          <View style={styles.scheduleModalOverlay}>
            <View style={styles.scheduleModalContent}>
              <View style={styles.scheduleModalHeader}>
                <Text style={styles.scheduleModalTitle}>📅 今日日程</Text>
                <TouchableOpacity onPress={() => setShowScheduleModal(false)}>
                  <Ionicons name="close" size={28} color="#333" />
                </TouchableOpacity>
              </View>
              <TouchableOpacity style={styles.refreshBtn} onPress={loadSchedules}>
                <Ionicons name="refresh" size={20} color="#667eea" />
                <Text style={styles.refreshText}>刷新</Text>
              </TouchableOpacity>
              <FlatList
                data={schedules}
                renderItem={renderScheduleItem}
                keyExtractor={(item, index) => item.id?.toString() || index.toString()}
                ListEmptyComponent={
                  <Text style={styles.emptySchedule}>暂无日程安排</Text>
                }
              />
            </View>
          </View>
        </Modal>
      </SafeAreaView>
    );
  }


  // WebView 页面
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
      
      {/* WebView 顶部栏 */}
      <View style={styles.webHeader}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => {
            setCurrentSite(null);
            setShowSiteList(true);
          }}
        >
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.webTitle} numberOfLines={1}>
          {currentSite?.name}
        </Text>
        <TouchableOpacity
          style={styles.headerBtn}
          onPress={() => setShowNotifications(!showNotifications)}
        >
          <Ionicons name="notifications-outline" size={24} color="#fff" />
          {notifications.length > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{notifications.length}</Text>
            </View>
          )}
        </TouchableOpacity>
      </View>

      {/* 通知下拉面板 */}
      <Animated.View style={[styles.notificationPanel, { transform: [{ translateY: slideAnim }] }]}>
        <View style={styles.notificationHeader}>
          <Text style={styles.notificationHeaderText}>消息通知</Text>
          <TouchableOpacity onPress={() => setNotifications([])}>
            <Text style={styles.clearBtn}>清空</Text>
          </TouchableOpacity>
        </View>
        <FlatList
          data={notifications}
          renderItem={renderNotificationItem}
          keyExtractor={item => item.id}
          ListEmptyComponent={
            <Text style={styles.emptyText}>暂无通知</Text>
          }
        />
      </Animated.View>

      {/* WebView */}
      <WebView
        source={{ uri: currentSite?.url }}
        style={styles.webview}
        startInLoadingState
        javaScriptEnabled
        domStorageEnabled
      />
    </SafeAreaView>
  );
}


// 包装组件，提供 SafeAreaProvider
export default function AppWrapper() {
  return (
    <SafeAreaProvider>
      <MainApp />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    paddingVertical: 15,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerBtn: {
    padding: 8,
    marginLeft: 10,
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    top: 2,
    right: 2,
    backgroundColor: '#ff4757',
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  notificationPanel: {
    position: 'absolute',
    top: 70,
    left: 10,
    right: 10,
    backgroundColor: '#fff',
    borderRadius: 12,
    maxHeight: 300,
    zIndex: 100,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  notificationHeaderText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  clearBtn: {
    color: '#667eea',
    fontSize: 14,
  },
  notificationItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  notificationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  notificationBody: {
    fontSize: 13,
    color: '#666',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    padding: 20,
  },
  siteList: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
    marginLeft: 5,
  },
  siteCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  siteIcon: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: '#f0f3ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  siteInfo: {
    flex: 1,
  },
  siteName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  siteUrl: {
    fontSize: 13,
    color: '#999',
  },
  addCard: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 30,
    marginTop: 10,
    borderWidth: 2,
    borderColor: '#e0e5ff',
    borderStyle: 'dashed',
  },
  addText: {
    marginTop: 10,
    fontSize: 15,
    color: '#667eea',
    fontWeight: '500',
  },

  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 25,
    width: width - 50,
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    marginBottom: 15,
    backgroundColor: '#f9f9f9',
    color: '#333',
  },
  modalBtns: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  modalBtn: {
    flex: 1,
    padding: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  cancelBtn: {
    backgroundColor: '#f0f0f0',
    marginRight: 10,
  },
  confirmBtn: {
    backgroundColor: '#667eea',
    marginLeft: 10,
  },
  cancelBtnText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scheduleModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  scheduleModalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: height * 0.7,
    paddingBottom: 30,
  },
  scheduleModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  scheduleModalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  refreshBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
  },
  refreshText: {
    color: '#667eea',
    marginLeft: 5,
    fontSize: 14,
  },
  scheduleItem: {
    flexDirection: 'row',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  scheduleTime: {
    width: 60,
    alignItems: 'center',
  },
  scheduleTimeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#667eea',
  },
  scheduleContent: {
    flex: 1,
    marginLeft: 15,
  },
  scheduleTitle: {
    fontSize: 15,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  scheduleDesc: {
    fontSize: 13,
    color: '#999',
  },
  emptySchedule: {
    textAlign: 'center',
    color: '#999',
    padding: 40,
    fontSize: 15,
  },
  webHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#667eea',
    paddingHorizontal: 10,
    paddingVertical: 12,
  },
  backBtn: {
    padding: 8,
  },
  webTitle: {
    flex: 1,
    fontSize: 17,
    fontWeight: '600',
    color: '#fff',
    marginLeft: 10,
  },
  webview: {
    flex: 1,
  },
});
