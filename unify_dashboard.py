import os

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\admin\dashboard.html"

unified_template = """{% extends 'base.html' %}
{% block title %}Admin Dashboard - ErrandExpress{% endblock %}

{% block content %}
<div class="admin-dashboard">
    <div class="dashboard-card">
        <div class="dashboard-header">
            <h1>📊 System Overview</h1>
            <p>Unified Operational Monitor</p>
        </div>

        <div class="dashboard-body">
            <!-- KPIS ROW -->
            <div class="kpi-row">
                <div class="kpi-item">
                    <span class="kpi-label">Users</span>
                    <span class="kpi-value">{{ total_users }}</span>
                    <span class="kpi-change">+{{ new_users_week }}</span>
                </div>
                <div class="kpi-item">
                    <span class="kpi-label">Tasks</span>
                    <span class="kpi-value">{{ total_tasks }}</span>
                    <span class="kpi-change">+{{ tasks_this_week }}</span>
                </div>
                <div class="kpi-item">
                    <span class="kpi-label">Revenue</span>
                    <span class="kpi-value">₱{{ total_revenue }}</span>
                    <span class="kpi-change">₱{{ revenue_this_month }}</span>
                </div>
                <div class="kpi-item">
                    <span class="kpi-label">Pending Skills</span>
                    <span class="kpi-value">{{ pending_skills }}</span>
                </div>
            </div>

            <hr class="divider">

            <!-- ANALYTICS GRID -->
            <div class="analytics-grid">
                <!-- Task Types -->
                <div class="analytics-col">
                    <h3>📂 Categories</h3>
                    <ul>
                    {% for category in category_stats %}
                        <li>
                            <span>{{ category.category|title }}</span>
                            <strong>{{ category.count }}</strong>
                        </li>
                    {% endfor %}
                    </ul>
                </div>

                <!-- Locations -->
                <div class="analytics-col">
                    <h3>📍 Campus Scope</h3>
                    <ul>
                    {% for campus in campus_stats %}
                        <li>
                            <span>{{ campus.campus_location|title|default:"Off-Campus" }}</span>
                            <strong>{{ campus.count }}</strong>
                        </li>
                    {% empty %}
                        <li class="empty">No data</li>
                    {% endfor %}
                    </ul>
                </div>

                <!-- Financials -->
                <div class="analytics-col">
                    <h3>💰 Revenue Source</h3>
                    <ul>
                    {% for rev in revenue_by_category %}
                        <li>
                            <span>{{ rev.task__category|title }}</span>
                            <strong>₱{{ rev.total_revenue|floatformat:2 }}</strong>
                        </li>
                    {% empty %}
                        <li class="empty">No data</li>
                    {% endfor %}
                    </ul>
                </div>
                
                <!-- Methods -->
                <div class="analytics-col">
                    <h3>💵 Payment Methods</h3>
                    <ul>
                    {% for method in payment_method_stats %}
                        <li>
                            <span>{% if method.payment_method == 'cod' %}COD{% else %}Online{% endif %}</span>
                            <strong>{{ method.count }}</strong>
                        </li>
                    {% empty %}
                        <li class="empty">No data</li>
                    {% endfor %}
                    </ul>
                </div>
            </div>
            
            <hr class="divider">
            
            <!-- ACTIONS ROW -->
            <div class="actions-row">
                <a href="{% url 'admin_users' %}" class="btn-action">Manage Users</a>
                <a href="{% url 'admin_tasks' %}" class="btn-action">Manage Tasks</a>
                <a href="{% url 'admin_skill_validation' %}" class="btn-action">Review Skills</a>
            </div>
        </div>
    </div>
</div>

<style>
    .admin-dashboard { padding: 2rem; max-width: 1400px; margin: 0 auto; }
    .dashboard-card { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }
    .dashboard-header { background: #f8f9fa; padding: 1.5rem 2rem; border-bottom: 1px solid #eee; text-align: center; }
    .dashboard-header h1 { margin: 0; font-size: 1.5rem; color: #2d3748; }
    .dashboard-header p { margin: 0.25rem 0 0; color: #718096; font-size: 0.9rem; }
    
    .dashboard-body { padding: 2rem; }
    
    .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; text-align: center; }
    .kpi-label { display: block; color: #718096; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
    .kpi-value { display: block; font-size: 2rem; font-weight: 700; color: #2d3748; }
    .kpi-change { font-size: 0.85rem; color: #48bb78; }
    
    .divider { border: 0; border-top: 1px solid #edf2f7; margin: 2rem 0; }
    
    .analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }
    .analytics-col h3 { font-size: 1rem; color: #4a5568; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
    .analytics-col ul { list-style: none; padding: 0; margin: 0; }
    .analytics-col li { display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px dashed #edf2f7; font-size: 0.95rem; }
    .analytics-col li:last-child { border-bottom: none; }
    .analytics-col strong { color: #2d3748; }
    .empty { color: #a0aec0; font-style: italic; }
    
    .actions-row { display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; }
    .btn-action { background: #667eea; color: white; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 500; transition: background 0.2s; }
    .btn-action:hover { background: #5a67d8; }
</style>
{% endblock %}
"""

print(f"Overwriting {file_path} with unified template...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(unified_template)

print("Dashboard successfully unified.")
