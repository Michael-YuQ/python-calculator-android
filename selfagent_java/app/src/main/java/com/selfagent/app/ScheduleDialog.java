package com.selfagent.app;

import android.app.Dialog;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class ScheduleDialog extends Dialog {
    
    private RecyclerView recyclerView;
    private ScheduleAdapter adapter;
    private List<Schedule> schedules = new ArrayList<>();
    private String apiUrl;
    private Handler handler = new Handler(Looper.getMainLooper());
    
    public ScheduleDialog(@NonNull Context context, String apiUrl) {
        super(context);
        this.apiUrl = apiUrl;
        
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.dialog_schedule);
        
        getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT, 
            (int)(context.getResources().getDisplayMetrics().heightPixels * 0.7));
        getWindow().setBackgroundDrawableResource(R.drawable.dialog_bg);
        
        recyclerView = findViewById(R.id.scheduleRecyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(context));
        adapter = new ScheduleAdapter(schedules);
        recyclerView.setAdapter(adapter);
        
        findViewById(R.id.closeBtn).setOnClickListener(v -> dismiss());
        findViewById(R.id.refreshBtn).setOnClickListener(v -> loadSchedules());
        
        loadSchedules();
    }
    
    private void loadSchedules() {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder().url(apiUrl).build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                handler.post(() -> Toast.makeText(getContext(), 
                    "加载失败", Toast.LENGTH_SHORT).show());
            }
            
            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful() && response.body() != null) {
                    String json = response.body().string();
                    List<Schedule> list = new Gson().fromJson(json, 
                        new TypeToken<List<Schedule>>(){}.getType());
                    handler.post(() -> {
                        schedules.clear();
                        if (list != null) schedules.addAll(list);
                        adapter.notifyDataSetChanged();
                    });
                }
            }
        });
    }
    
    static class Schedule {
        String id, time, title, content, description;
    }
    
    static class ScheduleAdapter extends RecyclerView.Adapter<ScheduleAdapter.ViewHolder> {
        private List<Schedule> items;
        
        ScheduleAdapter(List<Schedule> items) { this.items = items; }
        
        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_schedule, parent, false);
            return new ViewHolder(view);
        }
        
        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            Schedule s = items.get(position);
            holder.timeText.setText(s.time != null ? s.time : "--:--");
            holder.titleText.setText(s.title != null ? s.title : s.content);
            holder.descText.setText(s.description != null ? s.description : "");
            holder.descText.setVisibility(s.description != null ? View.VISIBLE : View.GONE);
        }
        
        @Override
        public int getItemCount() { return items.size(); }
        
        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView timeText, titleText, descText;
            ViewHolder(View v) {
                super(v);
                timeText = v.findViewById(R.id.scheduleTime);
                titleText = v.findViewById(R.id.scheduleTitle);
                descText = v.findViewById(R.id.scheduleDesc);
            }
        }
    }
}
