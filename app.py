from flask import Flask, render_template, request, redirect
import json
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__, template_folder="Templates")
#Route for home
@app.route("/")
def home():

    with open("expenses.json", "r") as file:
        expenses = json.load(file)

    category_expense = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category in category_expense:
            category_expense[category] += amount
        else:
            category_expense[category] = amount

    return render_template("index.html", expenses=expenses, category_expense=category_expense)

#route for add expenses
@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        name = request.form["name"].strip()
        amount = request.form["amount"].strip()
        category = request.form["category"].strip()
        date = request.form["date"].strip()

        # Check if any field is empty
        if not name or not amount or not category or not date:
            return render_template(
                "add_expense.html",
                error="Please fill in all the fields."
            )

        # Convert amount into a number
        amount = float(amount)

        expense = {
            "name": name,
            "amount": amount,
            "category": category,
            "date": date
        }

        with open("expenses.json", "r") as file:
            expenses = json.load(file)

        expenses.append(expense)

        with open("expenses.json", "w") as file:
            json.dump(expenses, file, indent=4)

        return redirect("/")

    return render_template("add_expense.html")
#Route for view expenses
@app.route("/view-expenses")
def view_expenses():
    with open("expenses.json", "r") as file:
        expenses = json.load(file)

    return render_template("view_expenses.html", expenses=expenses)

#Route for deleting the expenses
@app.route("/delete-expense/<int:index>")
def delete_expense(index):
    with open("expenses.json", "r") as file:
        expenses = json.load(file)

    if 0 <= index < len(expenses):
        expenses.pop(index)

    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=4)

    return redirect("/view-expenses")
#Route for analysis
@app.route("/analytics")
def analytics():

    with open("expenses.json", "r") as file:
        expenses = json.load(file)

    if not expenses:
        return render_template(
            "analytics.html",
            total_expense=0,
            highest_expense=0,
            lowest_expense=0,
            average_expense=0,
            category_expense={}
        )

    df = pd.DataFrame(expenses)

    total_expense = df["amount"].sum()
    highest_expense = df["amount"].max()
    lowest_expense = df["amount"].min()
    average_expense = df["amount"].mean()

    category_expense = df.groupby("category")["amount"].sum().to_dict()

    categories = list(category_expense.keys())
    amounts = list(category_expense.values())

    plt.figure(figsize=(8, 5))
    plt.bar(categories, amounts, color="#A7F950")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.title("Category-wise Expense")
    plt.tight_layout()

    plt.savefig("static/expense_chart.png")
    plt.close()

    return render_template(
        "analytics.html",
        total_expense=total_expense,
        highest_expense=highest_expense,
        lowest_expense=lowest_expense,
        average_expense=average_expense,
        category_expense=category_expense
    )
# Route for settings
@app.route("/settings")
def settings():
    return render_template("settings.html")
# Route for clearing all expenses
@app.route("/clear-expenses")
def clear_expenses():

    with open("expenses.json", "w") as file:
        json.dump([], file, indent=4)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
