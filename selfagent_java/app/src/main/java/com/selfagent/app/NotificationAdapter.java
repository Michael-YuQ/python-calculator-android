package com.selfagent.app;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

public class NotificationAdapter extends RecyclerView.Adapter<NotificationAdapter.ViewHolder> {
    
    private List<MainActivity.NotificationItem> items;
    
    public NotificationAdapter(List<MainActivity.NotificationItem> items) {
        this.items = items;
    }
    
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_notification, parent, false);
        return new ViewHolder(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        MainActivity.NotificationItem item = items.get(position);
        holder.titleText.setText(item.title);
        holder.bodyText.setText(item.body);
    }
    
    @Override
    public int getItemCount() {
        return items.size();
    }
    
    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView titleText, bodyText;
        
        ViewHolder(View view) {
            super(view);
            titleText = view.findViewById(R.id.notificationTitle);
            bodyText = view.findViewById(R.id.notificationBody);
        }
    }
}
