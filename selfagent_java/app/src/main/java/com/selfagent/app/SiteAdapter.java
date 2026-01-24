package com.selfagent.app;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;
import java.util.function.Consumer;

public class SiteAdapter extends RecyclerView.Adapter<SiteAdapter.ViewHolder> {
    
    private List<MainActivity.Site> sites;
    private Consumer<MainActivity.Site> onClick;
    private Consumer<MainActivity.Site> onLongClick;
    
    public SiteAdapter(List<MainActivity.Site> sites, 
                       Consumer<MainActivity.Site> onClick,
                       Consumer<MainActivity.Site> onLongClick) {
        this.sites = sites;
        this.onClick = onClick;
        this.onLongClick = onLongClick;
    }
    
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_site, parent, false);
        return new ViewHolder(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        MainActivity.Site site = sites.get(position);
        holder.nameText.setText(site.name);
        holder.urlText.setText(site.url);
        
        holder.itemView.setOnClickListener(v -> onClick.accept(site));
        holder.itemView.setOnLongClickListener(v -> {
            onLongClick.accept(site);
            return true;
        });
    }
    
    @Override
    public int getItemCount() {
        return sites.size();
    }
    
    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView nameText, urlText;
        
        ViewHolder(View view) {
            super(view);
            nameText = view.findViewById(R.id.siteName);
            urlText = view.findViewById(R.id.siteUrl);
        }
    }
}
