package com.selfagent.app;

import android.app.AlertDialog;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.util.ArrayList;
import java.util.List;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;

public class MainActivity extends AppCompatActivity {
    
    private static final String WS_URL = "ws://111.170.6.103:9999/ws";
    private static final String SCHEDULE_API = "http://111.170.6.103:9999/api/daily.php";
    private static final String CHANNEL_ID = "selfagent_channel";
    private static final String PREFS_NAME = "SelfAgentPrefs";
    private static final String SITES_KEY = "sites";
    
    private RecyclerView sitesRecyclerView;
    private SiteAdapter siteAdapter;
    private List<Site> sites = new ArrayList<>();
    private List<NotificationItem> notifications = new ArrayList<>();
    
    private WebSocket webSocket;
    private OkHttpClient client;
    private Handler handler = new Handler(Looper.getMainLooper());
    private Gson gson = new Gson();
    private boolean wsConnected = false;
    
    private View notificationPanel;
    private RecyclerView notificationRecyclerView;
    private NotificationAdapter notificationAdapter;
    private TextView badgeText;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        createNotificationChannel();
        initViews();
        loadSites();
        connectWebSocket();
    }
    
    private void initViews() {
        sitesRecyclerView = findViewById(R.id.sitesRecyclerView);
        sitesRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        siteAdapter = new SiteAdapter(sites, this::openSite, this::deleteSite);
        sitesRecyclerView.setAdapter(siteAdapter);
        
        // 通知面板
        notificationPanel = findViewById(R.id.notificationPanel);
        notificationRecyclerView = findViewById(R.id.notificationRecyclerView);
        notificationRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        notificationAdapter = new NotificationAdapter(notifications);
        notificationRecyclerView.setAdapter(notificationAdapter);
        
        badgeText = findViewById(R.id.badgeText);
        
        // 添加站点按钮
        findViewById(R.id.addSiteBtn).setOnClickListener(v -> showAddSiteDialog());
        
        // 日程按钮
        findViewById(R.id.scheduleBtn).setOnClickListener(v -> showScheduleDialog());
        
        // 通知按钮
        findViewById(R.id.notificationBtn).setOnClickListener(v -> toggleNotificationPanel());
        
        // 清空通知
        findViewById(R.id.clearNotificationsBtn).setOnClickListener(v -> {
            notifications.clear();
            notificationAdapter.notifyDataSetChanged();
            updateBadge();
        });
    }
    
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID, "SelfAgent通知", NotificationManager.IMPORTANCE_HIGH);
            channel.setDescription("接收消息推送");
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
    }
    
    private void loadSites() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String json = prefs.getString(SITES_KEY, null);
        if (json != null) {
            List<Site> saved = gson.fromJson(json, new TypeToken<List<Site>>(){}.getType());
            if (saved != null) {
                sites.clear();
                sites.addAll(saved);
            }
        }
        if (sites.isEmpty()) {
            sites.add(new Site("1", "主系统", "http://111.170.6.103:9999/"));
        }
        siteAdapter.notifyDataSetChanged();
    }
    
    private void saveSites() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(SITES_KEY, gson.toJson(sites)).apply();
    }
    
    private void showAddSiteDialog() {
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_add_site, null);
        EditText nameInput = dialogView.findViewById(R.id.siteNameInput);
        EditText urlInput = dialogView.findViewById(R.id.siteUrlInput);
        
        new AlertDialog.Builder(this)
            .setTitle("添加站点")
            .setView(dialogView)
            .setPositiveButton("添加", (d, w) -> {
                String name = nameInput.getText().toString().trim();
                String url = urlInput.getText().toString().trim();
                if (name.isEmpty() || url.isEmpty()) {
                    Toast.makeText(this, "请填写完整信息", Toast.LENGTH_SHORT).show();
                    return;
                }
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    url = "http://" + url;
                }
                sites.add(new Site(String.valueOf(System.currentTimeMillis()), name, url));
                siteAdapter.notifyDataSetChanged();
                saveSites();
            })
            .setNegativeButton("取消", null)
            .show();
    }
    
    private void openSite(Site site) {
        WebViewActivity.start(this, site.name, site.url);
    }
    
    private void deleteSite(Site site) {
        new AlertDialog.Builder(this)
            .setTitle("确认删除")
            .setMessage("确定要删除 " + site.name + " 吗？")
            .setPositiveButton("删除", (d, w) -> {
                sites.remove(site);
                siteAdapter.notifyDataSetChanged();
                saveSites();
            })
            .setNegativeButton("取消", null)
            .show();
    }
    
    private void toggleNotificationPanel() {
        if (notificationPanel.getVisibility() == View.VISIBLE) {
            notificationPanel.setVisibility(View.GONE);
        } else {
            notificationPanel.setVisibility(View.VISIBLE);
        }
    }
    
    private void updateBadge() {
        if (notifications.isEmpty()) {
            badgeText.setVisibility(View.GONE);
        } else {
            badgeText.setVisibility(View.VISIBLE);
            badgeText.setText(String.valueOf(notifications.size()));
        }
    }
    
    private void showScheduleDialog() {
        ScheduleDialog dialog = new ScheduleDialog(this, SCHEDULE_API);
        dialog.show();
    }
    
    private void connectWebSocket() {
        client = new OkHttpClient();
        Request request = new Request.Builder().url(WS_URL).build();
        
        webSocket = client.newWebSocket(request, new WebSocketListener() {
            @Override
            public void onOpen(WebSocket ws, Response response) {
                wsConnected = true;
                handler.post(() -> Toast.makeText(MainActivity.this, 
                    "已连接服务器", Toast.LENGTH_SHORT).show());
            }
            
            @Override
            public void onMessage(WebSocket ws, String text) {
                handler.post(() -> handleMessage(text));
            }
            
            @Override
            public void onClosed(WebSocket ws, int code, String reason) {
                wsConnected = false;
                handler.postDelayed(() -> connectWebSocket(), 5000);
            }
            
            @Override
            public void onFailure(WebSocket ws, Throwable t, Response response) {
                wsConnected = false;
                handler.postDelayed(() -> connectWebSocket(), 5000);
            }
        });
    }
    
    private void handleMessage(String text) {
        String title = "📢 新消息";
        String body = text;
        
        try {
            WsMessage msg = gson.fromJson(text, WsMessage.class);
            if (msg.title != null) title = msg.title;
            if (msg.message != null) body = msg.message;
            else if (msg.body != null) body = msg.body;
        } catch (Exception ignored) {}
        
        // 添加到列表
        notifications.add(0, new NotificationItem(title, body));
        notificationAdapter.notifyDataSetChanged();
        updateBadge();
        
        // 系统通知
        showNotification(title, body);
    }
    
    private void showNotification(String title, String body) {
        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true);
        
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.notify((int) System.currentTimeMillis(), builder.build());
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (webSocket != null) webSocket.close(1000, "App closed");
    }
    
    // 数据类
    static class Site {
        String id, name, url;
        Site(String id, String name, String url) {
            this.id = id; this.name = name; this.url = url;
        }
    }
    
    static class NotificationItem {
        String title, body;
        NotificationItem(String title, String body) {
            this.title = title; this.body = body;
        }
    }
    
    static class WsMessage {
        String title, message, body;
    }
}
