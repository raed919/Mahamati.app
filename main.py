import flet as ft
import json
import os

# --- إعداد ملف الخزن الدائم ---
DB_FILE = "tasks_db.json"

def get_all_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_all_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    # إعدادات شاشة الموبايل (حجم ثابت وتصميم عمودي)
    page.title = "مهماتي - موبايل"
    page.window_width = 380
    page.window_height = 740
    page.horizontal_alignment = "center"
    page.theme_mode = "light"

    PRIMARY = "#4F46E5"
    SECONDARY = "#0D9488" 
    SUCCESS = "#10B981"
    URGENT = "#E11D48"

    def load_tasks(room_name):
        return get_all_data().get(room_name, [])

    def save_tasks(room_name, tasks):
        data = get_all_data()
        data[room_name] = tasks
        save_all_data(data)

    def toggle_theme(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    # ==========================================
    # 1. شاشة القفل
    # ==========================================
    def show_login():
        page.clean()
        pin_field = ft.TextField(label="أدخل الرمز السري", password=True, width=250, text_align="center", border_radius=10)
        msg = ft.Text("", color="red")

        def validate_pin(e):
            if pin_field.value == "1234":
                show_dashboard()
            else:
                msg.value = "الرمز السري خطأ!"
                page.update()

        page.add(
            ft.Container(height=80),
            ft.Text("🔒", size=80),
            ft.Text("تطبيق مهماتي", size=28, weight="bold", color=PRIMARY),
            ft.Text("الوصول الآمن (نسخة الموبايل)", size=16, color="grey"),
            msg,
            pin_field,
            ft.ElevatedButton("دخول", on_click=validate_pin, style=ft.ButtonStyle(bgcolor=PRIMARY, color="white"), width=250, height=45)
        )

    # ==========================================
    # 2. لوحة التحكم
    # ==========================================
    def show_dashboard():
        page.clean()
        data = get_all_data()
        
        total = 0; done = 0; urgent = 0
        for room_tasks in data.values():
            for t in room_tasks:
                total += 1
                if t.get('done'): done += 1
                if t.get('urgent') and not t.get('done'): urgent += 1

        bg_summary = "#f3f4f6" if page.theme_mode == "light" else "#1f2937"

        page.add(
            ft.Row([
                ft.Container(content=ft.Text("🌙", size=24), on_click=toggle_theme, ink=True, padding=5),
                ft.Container(expand=True),
                ft.Text("لوحة التحكم", size=24, weight="bold", color=PRIMARY),
            ], width=340),
            ft.Divider(),

            ft.Container(
                content=ft.Column([
                    ft.Text("ملخص المهام 📊", weight="bold", size=18, color=PRIMARY),
                    ft.Row([
                        ft.Text(f"🔥 مستعجلة: {urgent}", color=URGENT, weight="bold"),
                        ft.Text(f"✅ منجزة: {done}", color=SUCCESS, weight="bold"),
                        ft.Text(f"📈 إجمالي: {total}", color=PRIMARY, weight="bold"),
                    ], alignment="center", spacing=15)
                ], horizontal_alignment="center"),
                bgcolor=bg_summary, padding=15, border_radius=15, border=ft.border.all(1, PRIMARY), width=340
            ),
            ft.Divider(),

            ft.Row([
                ft.ElevatedButton("👔 العميد", width=160, height=100, bgcolor=PRIMARY, color="white", on_click=lambda e: show_tasks("غرفة العميد")),
                ft.ElevatedButton("🎓 الطلاب", width=160, height=100, bgcolor=PRIMARY, color="white", on_click=lambda e: show_tasks("غرفة الطلاب")),
            ], alignment="center"),
            ft.Row([
                ft.ElevatedButton("🏡 العائلة", width=160, height=100, bgcolor=PRIMARY, color="white", on_click=lambda e: show_tasks("العائلة")),
                ft.ElevatedButton("💼 الموظفين", width=160, height=100, bgcolor=PRIMARY, color="white", on_click=lambda e: show_tasks("غرفة الموظفين")),
            ], alignment="center"),
            
            ft.Container(height=10),
            ft.ElevatedButton("📊 جدول ملخص المهام العام", width=330, height=50, style=ft.ButtonStyle(bgcolor=SECONDARY, color="white"), on_click=lambda e: show_summary())
        )

    # ==========================================
    # 3. شاشة المهام (مع ميزة الأزرار التفاعلية 💡)
    # ==========================================
    def show_tasks(room_name):
        page.clean()
        current_tasks = load_tasks(room_name)

        task_input = ft.TextField(label="اكتب المهمة هنا...", width=220, border_radius=10, text_align="right")
        time_input = ft.TextField(label="الوقت", width=100, border_radius=10, text_align="center")
        urgent_check = ft.Checkbox(label="🔥 مستعجل", value=False, fill_color=URGENT)
        
        selected_cat = "📝 امتحانات"

        btn_assignments = ft.ElevatedButton("📑 واجبات", width=100, on_click=lambda e: set_cat("📑 واجبات"))
        btn_lectures = ft.ElevatedButton("📚 محاضرات", width=100, on_click=lambda e: set_cat("📚 محاضرات"))
        btn_exams = ft.ElevatedButton("📝 امتحانات", width=100, on_click=lambda e: set_cat("📝 امتحانات"))

        def update_tabs_ui():
            unselected_bg = "#f3f4f6" if page.theme_mode == "light" else "#374151"
            unselected_text = "grey"

            btn_exams.bgcolor = "red" if selected_cat == "📝 امتحانات" else unselected_bg
            btn_exams.color = "white" if selected_cat == "📝 امتحانات" else unselected_text

            btn_lectures.bgcolor = "green" if selected_cat == "📚 محاضرات" else unselected_bg
            btn_lectures.color = "white" if selected_cat == "📚 محاضرات" else unselected_text

            btn_assignments.bgcolor = "blue" if selected_cat == "📑 واجبات" else unselected_bg
            btn_assignments.color = "white" if selected_cat == "📑 واجبات" else unselected_text

        def set_cat(c):
            nonlocal selected_cat
            selected_cat = c
            update_tabs_ui() 
            refresh_list()
        
        update_tabs_ui() 

        cat_tabs = ft.Row([btn_assignments, btn_lectures, btn_exams], scroll="auto")

        status_text = ft.Text("", size=15, weight="bold", color="grey")
        tasks_list_view = ft.Column(scroll="auto", expand=True, width=340)

        def refresh_list():
            tasks_list_view.controls.clear()
            
            display_tasks = current_tasks
            if room_name == "غرفة الطلاب":
                display_tasks = [t for t in current_tasks if t.get('cat') == selected_cat]

            total_in_view = len(display_tasks)
            done_in_view = sum(1 for t in display_tasks if t.get('done'))
            
            if total_in_view == 0:
                status_text.value = "🍃 لا توجد مهام حالياً"
            else:
                status_text.value = f"📊 تم إنجاز {done_in_view} من أصل {total_in_view} مهام"

            for i, task in enumerate(current_tasks):
                if room_name == "غرفة الطلاب" and task.get('cat') != selected_cat:
                    continue

                def delete_task(e, index=i):
                    current_tasks.pop(index)
                    save_tasks(room_name, current_tasks)
                    refresh_list()

                def toggle_task(e, t=task):
                    t['done'] = e.control.value
                    save_tasks(room_name, current_tasks)
                    refresh_list()
                
                prefix = "🔥 " if task.get('urgent') and not task.get('done') else ""
                
                row = ft.Row([
                    ft.Container(
                        content=ft.Checkbox(label=f"{prefix}{task['title']} ({task['time']})", value=task.get('done', False), on_change=toggle_task, fill_color=SUCCESS if task.get('done') else PRIMARY),
                        expand=True
                    ),
                    ft.Container(content=ft.Text("🗑️", size=22), on_click=delete_task, ink=True, padding=5)
                ], alignment="spaceBetween")
                
                bg_task = "#D1FAE5" if task.get('done') else ("#f9f9f9" if page.theme_mode == "light" else "#374151")
                
                tasks_list_view.controls.append(
                    ft.Container(content=row, padding=5, bgcolor=bg_task, border_radius=8, margin=ft.margin.only(bottom=5))
                )
            page.update()

        def add_task(e):
            if task_input.value != "":
                current_tasks.append({
                    "title": task_input.value, 
                    "time": time_input.value or "-", 
                    "done": False,
                    "urgent": urgent_check.value,
                    "cat": selected_cat if room_name == "غرفة الطلاب" else ""
                })
                save_tasks(room_name, current_tasks)
                task_input.value = ""
                time_input.value = ""
                urgent_check.value = False
                refresh_list()

        elements = [
            ft.Row([
                ft.Container(content=ft.Text("⬅️", size=24), on_click=lambda e: show_dashboard(), ink=True, padding=5),
                ft.Container(expand=True),
                ft.Text(f"📍 {room_name}", size=22, weight="bold", color=PRIMARY)
            ], width=340),
            ft.Divider()
        ]

        if room_name == "غرفة الطلاب":
            elements.append(cat_tabs)
            elements.append(ft.Divider())

        elements.extend([
            ft.Row([time_input, task_input], alignment="center", width=340),
            ft.Row([urgent_check], alignment="end", width=340),
            ft.ElevatedButton("إضافة المهمة ➕", width=330, height=45, style=ft.ButtonStyle(bgcolor=PRIMARY, color="white"), on_click=add_task),
            ft.Container(height=10),
            ft.Row([ft.Container(expand=True), status_text], width=340),
            tasks_list_view
        ])

        page.add(*elements)
        refresh_list()

    # ==========================================
    # 4. شاشة جدول ملخص المهام العام 
    # ==========================================
    def show_summary():
        page.clean()
        data = get_all_data()

        rows = ft.Column(scroll="auto", expand=True, width=350)
        
        has_tasks = False
        for room, tasks in data.items():
            for t in tasks:
                has_tasks = True
                if t.get('done'):
                    status = "✅ منجزة"
                    status_color = SUCCESS
                elif t.get('urgent'):
                    status = "🔥 مستعجلة"
                    status_color = URGENT
                else:
                    status = "⏳ انتظار"
                    status_color = "grey"

                short_room = room.replace("غرفة ", "")
                if t.get('cat'):
                    short_room += f" {t.get('cat').split()[0]}" 

                rows.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(status, color=status_color, weight="bold", width=80, text_align="center"),
                            ft.Text(t['title'], expand=True, text_align="right", weight="bold"),
                            ft.Text(short_room, width=70, text_align="right", color="grey", size=12),
                        ]),
                        bgcolor="white" if page.theme_mode == "light" else "#374151",
                        padding=10, border_radius=8, border=ft.border.all(1, "#E5E7EB")
                    )
                )

        if not has_tasks:
            rows.controls.append(ft.Text("لا توجد مهام مسجلة حالياً 🍃", text_align="center", color="grey", size=16))

        page.add(
            ft.Row([
                ft.Container(content=ft.Text("⬅️", size=24), on_click=lambda e: show_dashboard(), ink=True, padding=5),
                ft.Container(expand=True),
                ft.Text("الجدول العام 📊", size=24, weight="bold", color=PRIMARY)
            ], width=340),
            ft.Divider(),
            ft.Container(content=rows, padding=5, border_radius=10, expand=True)
        )

    show_login()

ft.app(target=main)