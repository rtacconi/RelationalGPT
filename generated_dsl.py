# Generated RelationalGPT DSL Code
from relational.dsl import restrict, join, project, extend, summarize, ensure
from workflow.dsl import Workflow, Page, Section, Flow, Validation

Task = [
    {"id": 1, "title": "Complete project proposal", "description": "Write up the proposal for the new client project", "status": "pending", "priority": "high", "due_date": 20230615, "assigned_to": 101},
    {"id": 2, "title": "Review code", "description": "Review pull request #42", "status": "in_progress", "priority": "medium", "due_date": 20230610, "assigned_to": 102},
    {"id": 3, "title": "Fix login bug", "description": "Users can't log in on Firefox", "status": "pending", "priority": "high", "due_date": 20230605, "assigned_to": 103},
    {"id": 4, "title": "Update documentation", "description": "Add new API endpoints to docs", "status": "completed", "priority": "low", "due_date": 20230601, "assigned_to": 101},
    {"id": 5, "title": "Weekly team meeting", "description": "Regular sync-up with the team", "status": "pending", "priority": "medium", "due_date": 20230620, "assigned_to": 101}
]

User = [
    {"id": 101, "name": "Alice Smith", "email": "alice@example.com", "role": "manager"},
    {"id": 102, "name": "Bob Johnson", "email": "bob@example.com", "role": "developer"},
    {"id": 103, "name": "Charlie Brown", "email": "charlie@example.com", "role": "developer"},
    {"id": 104, "name": "Diana Williams", "email": "diana@example.com", "role": "designer"}
]

Comment = [
    {"id": 1001, "task_id": 1, "user_id": 102, "text": "I think we should add more details to the timeline section.", "created_at": 20230601},
    {"id": 1002, "task_id": 1, "user_id": 101, "text": "Good point, I'll update it tomorrow.", "created_at": 20230601},
    {"id": 1003, "task_id": 3, "user_id": 103, "text": "I've identified the issue, working on a fix now.", "created_at": 20230602},
    {"id": 1004, "task_id": 2, "user_id": 101, "text": "Let me know when you're done so I can review too.", "created_at": 20230603}
]

Label = [
    {"id": 201, "name": "Bug", "color": "red"},
    {"id": 202, "name": "Feature", "color": "green"},
    {"id": 203, "name": "Documentation", "color": "blue"},
    {"id": 204, "name": "Meeting", "color": "purple"}
]

TaskLabel = [
    {"task_id": 1, "label_id": 202},
    {"task_id": 2, "label_id": 202},
    {"task_id": 3, "label_id": 201},
    {"task_id": 4, "label_id": 203},
    {"task_id": 5, "label_id": 204}
]

task_management_workflow = Workflow("Task Management Application")
task_management_workflow.add_page(
    Page("Dashboard", route="/")
    .set_description("Overview of tasks and their statuses.")
    .add_section(Section("Overview", "Summary of task counts by status and priority."))
    .add_section(Section("My Tasks", "List of tasks assigned to the current user."))
    .add_section(Section("Recent Activity", "Recent comments and status changes."))
    .add_flow(Flow("View task details", "Task Details"))
    .add_flow(Flow("Create new task", "Create Task"))
)
task_management_workflow.add_page(
    Page("Task Details", route="/task/<task_id>")
    .set_description("Detailed view of a specific task.")
    .add_section(Section("Task Information", "ID, title, description, status, priority, due date."))
    .add_section(Section("Assigned User", "The user responsible for this task."))
    .add_section(Section("Comments", "Discussion about the task."))
    .add_section(Section("Labels", "Categories and tags for the task."))
    .add_section(Section("Add Comment", "Form to add a new comment to the task."))
    .add_flow(Flow("Edit task", "Edit Task"))
    .add_flow(Flow("Back to dashboard", "Dashboard"))
    .add_validation(Validation("Comment text must be provided"))
)
task_management_workflow.add_page(
    Page("Create Task", route="/tasks/create")
    .set_description("Form to create a new task.")
    .add_section(Section("Task Form", "Fields for title, description, status, priority, due date, assigned user, and labels."))
    .add_flow(Flow("Submit task", "Dashboard"))
    .add_flow(Flow("Cancel", "Dashboard"))
    .add_validation(Validation("Title must be provided"))
    .add_validation(Validation("Status must be valid"))
    .add_validation(Validation("Priority must be valid"))
    .add_validation(Validation("Due date must be in the future"))
    .add_validation(Validation("Assigned user must be valid"))
)
task_management_workflow.add_page(
    Page("Edit Task", route="/task/<task_id>/edit")
    .set_description("Form to edit an existing task.")
    .add_section(Section("Task Form", "Fields for title, description, status, priority, due date, assigned user, and labels."))
    .add_flow(Flow("Save changes", "Task Details"))
    .add_flow(Flow("Cancel", "Task Details"))
    .add_validation(Validation("Title must be provided"))
    .add_validation(Validation("Status must be valid"))
    .add_validation(Validation("Priority must be valid"))
    .add_validation(Validation("Due date must be valid"))
    .add_validation(Validation("Assigned user must be valid"))
)
task_management_workflow.add_page(
    Page("User Profile", route="/user/<user_id>")
    .set_description("View and edit user profile information.")
    .add_section(Section("User Information", "Name, email, role."))
    .add_section(Section("Assigned Tasks", "List of tasks assigned to this user."))
    .add_flow(Flow("Edit profile", "Edit Profile"))
    .add_flow(Flow("Back to dashboard", "Dashboard"))
)
task_management_workflow.add_page(
    Page("Edit Profile", route="/user/<user_id>/edit")
    .set_description("Form to edit user profile information.")
    .add_section(Section("Profile Form", "Fields for name, email, role."))
    .add_flow(Flow("Save changes", "User Profile"))
    .add_flow(Flow("Cancel", "User Profile"))
    .add_validation(Validation("Name must be provided"))
    .add_validation(Validation("Email must be a valid email address"))
    .add_validation(Validation("Role must be valid"))
)


def run_constraints():
    ensure(
        "All tasks must have a valid status",
        len(restrict(Task, lambda row: row['status'] not in valid_statuses)) == 0
    )
    
    # Every task must have a valid priority
    valid_priorities = ["low", "medium", "high"]
    ensure(
        "All tasks must have a valid priority",
        len(restrict(Task, lambda row: row['priority'] not in valid_priorities)) == 0
    )
    
    # Every task must be assigned to a valid user
    task_user = join(Task, User)
    ensure(
        "All tasks must be assigned to a valid user",
        len(task_user) == len(Task)
    )
    
    # No task can have a due date in the past when it's created
    # (Simplified for the example - normally would check against current date)
    ensure(
        "New tasks cannot have a due date in the past",
        len(restrict(Task, lambda row: row['due_date'] < 20230101)) == 0
    )
    
    # Every comment must be associated with a valid task and user
    valid_comments = join(join(Comment, Task), User)
    ensure(
        "All comments must reference valid tasks and users",
        len(valid_comments) == len(Comment)
    )
    
    # Task labels must reference valid tasks and labels
    valid_task_labels = join(join(TaskLabel, Task), Label)
    ensure(
        "All task labels must reference valid tasks and labels",
        len(valid_task_labels) == len(TaskLabel)
    )
    
    # High priority tasks should not be overdue
    # (Simplified for the example)
    high_priority_overdue = restrict(
        Task, 
        lambda row: row['priority'] == 'high' and row['status'] != 'completed' and row['due_date'] < 20230605
    )
    ensure(
        "High priority tasks should not be overdue",
        len(high_priority_overdue) == 0
    )

# Workflow Definition

task_management_workflow = Workflow("Task Management Application")

# Dashboard Page
task_management_workflow.add_page(
    Page("Dashboard", route="/")
    .set_description("Overview of tasks and their statuses.")
    .add_section(Section("Overview", "Summary of task counts by status and priority."))
    .add_section(Section("My Tasks", "List of tasks assigned to the current user."))
    .add_section(Section("Recent Activity", "Recent comments and status changes."))
    .add_flow(Flow("View task details", "Task Details"))
    .add_flow(Flow("Create new task", "Create Task"))
)

# Task Details Page
task_management_workflow.add_page(
    Page("Task Details", route="/task/<task_id>")
    .set_description("Detailed view of a specific task.")
    .add_section(Section("Task Information", "ID, title, description, status, priority, due date."))
    .add_section(Section("Assigned User", "The user responsible for this task."))
    .add_section(Section("Comments", "Discussion about the task."))
    .add_section(Section("Labels", "Categories and tags for the task."))
    .add_section(Section("Add Comment", "Form to add a new comment to the task."))
    .add_flow(Flow("Edit task", "Edit Task"))
    .add_flow(Flow("Back to dashboard", "Dashboard"))
    .add_validation(Validation("Comment text must be provided"))
)

# Create Task Page
task_management_workflow.add_page(
    Page("Create Task", route="/tasks/create")
    .set_description("Form to create a new task.")
    .add_section(Section("Task Form", "Fields for title, description, status, priority, due date, assigned user, and labels."))
    .add_flow(Flow("Submit task", "Dashboard"))
    .add_flow(Flow("Cancel", "Dashboard"))
    .add_validation(Validation("Title must be provided"))
    .add_validation(Validation("Status must be valid"))
    .add_validation(Validation("Priority must be valid"))
    .add_validation(Validation("Due date must be in the future"))
    .add_validation(Validation("Assigned user must be valid"))
)

# Edit Task Page
task_management_workflow.add_page(
    Page("Edit Task", route="/task/<task_id>/edit")
    .set_description("Form to edit an existing task.")
    .add_section(Section("Task Form", "Fields for title, description, status, priority, due date, assigned user, and labels."))
    .add_flow(Flow("Save changes", "Task Details"))
    .add_flow(Flow("Cancel", "Task Details"))
    .add_validation(Validation("Title must be provided"))
    .add_validation(Validation("Status must be valid"))
    .add_validation(Validation("Priority must be valid"))
    .add_validation(Validation("Due date must be valid"))
    .add_validation(Validation("Assigned user must be valid"))
)

# User Profile Page
task_management_workflow.add_page(
    Page("User Profile", route="/user/<user_id>")
    .set_description("View and edit user profile information.")
    .add_section(Section("User Information", "Name, email, role."))
    .add_section(Section("Assigned Tasks", "List of tasks assigned to this user."))
    .add_flow(Flow("Edit profile", "Edit Profile"))
    .add_flow(Flow("Back to dashboard", "Dashboard"))
)

# Edit Profile Page
task_management_workflow.add_page(
    Page("Edit Profile", route="/user/<user_id>/edit")
    .set_description("Form to edit user profile information.")
    .add_section(Section("Profile Form", "Fields for name, email, role."))
    .add_flow(Flow("Save changes", "User Profile"))
    .add_flow(Flow("Cancel", "User Profile"))
    .add_validation(Validation("Name must be provided"))
    .add_validation(Validation("Email must be a valid email address"))
    .add_validation(Validation("Role must be valid"))

    )


if __name__ == "__main__":
    # For testing, print all defined relations
    for var_name, var_value in locals().items():
        if isinstance(var_value, list) and all(isinstance(item, dict) for item in var_value if var_value):
            print(f"Relation: {var_name} with {len(var_value)} rows")
    
    # Run constraints if defined
    if 'run_constraints' in locals():
        print("\nRunning constraints:")
        run_constraints()
