from models import db, logger
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

todo = Blueprint("todo", __name__, url_prefix="/todo")


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@todo.route("/")
def todo_app():
    logger.debug("Index request")
    todo_list = Todo.query.all()
    logger.debug(todo_list)
    if current_user.get_id() is not None:
        return render_template("todo_app.html", todo_list=todo_list, username=current_user.get_id())
    return render_template("todo_app.html", todo_list=todo_list)


@todo.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    logger.debug("Add " + title)
    return redirect(url_for("todo.todo_app"))


@todo.route("/update/<int:todo_id>")
def update(todo_id):
    logger.debug("Update request  id: " + str(todo_id))
    active_todo = Todo.query.filter_by(id=todo_id).first()
    active_todo.complete = not active_todo.complete
    db.session.commit()
    return redirect(url_for("todo.todo_app"))


@todo.route("/delete/<int:todo_id>")
def delete(todo_id):
    logger.debug("Delete request  id: " + str(todo_id))
    active_todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(active_todo)
    db.session.commit()
    return redirect(url_for("todo.todo_app"))
