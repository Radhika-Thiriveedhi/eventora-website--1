from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Budget, Expense, Event
from app.utils.decorators import organizer_required

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/event/<int:eid>')
@login_required
@organizer_required
def view(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('events.index'))
    budget = Budget.query.filter_by(event_id=eid).first()
    expenses = budget.expenses.all() if budget else []
    total_estimated = sum(e.estimated_amount or 0 for e in expenses)
    total_actual = sum(e.actual_amount or 0 for e in expenses)
    remaining = (budget.total_budget - total_actual) if budget else 0
    categories = ['venue', 'catering', 'decoration', 'photography',
                  'lighting', 'music', 'transport', 'other']
    return render_template('budget/view.html', event=event, budget=budget,
                           expenses=expenses, total_estimated=total_estimated,
                           total_actual=total_actual, remaining=remaining,
                           categories=categories)


@budget_bp.route('/event/<int:eid>/set', methods=['POST'])
@login_required
@organizer_required
def set_budget(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('events.index'))
    amount = float(request.form.get('total_budget', 0))
    budget = Budget.query.filter_by(event_id=eid).first()
    if budget:
        budget.total_budget = amount
        budget.notes = request.form.get('notes', budget.notes)
    else:
        budget = Budget(event_id=eid, total_budget=amount,
                        notes=request.form.get('notes'))
        db.session.add(budget)
    db.session.commit()
    flash('Budget set!', 'success')
    return redirect(url_for('budget.view', eid=eid))


@budget_bp.route('/event/<int:eid>/add-expense', methods=['POST'])
@login_required
@organizer_required
def add_expense(eid):
    budget = Budget.query.filter_by(event_id=eid).first()
    if not budget:
        flash('Set a budget for this event first.', 'warning')
        return redirect(url_for('budget.view', eid=eid))
    exp = Expense(
        budget_id=budget.id,
        category=request.form.get('category', 'other'),
        description=request.form.get('description', '').strip(),
        estimated_amount=float(request.form.get('estimated_amount') or 0),
        actual_amount=float(request.form.get('actual_amount') or 0),
        paid=bool(request.form.get('paid'))
    )
    db.session.add(exp)
    db.session.commit()
    flash('Expense added!', 'success')
    return redirect(url_for('budget.view', eid=eid))


@budget_bp.route('/expense/<int:expid>/delete', methods=['POST'])
@login_required
@organizer_required
def delete_expense(expid):
    exp = Expense.query.get_or_404(expid)
    budget = Budget.query.get(exp.budget_id)
    eid = budget.event_id
    db.session.delete(exp)
    db.session.commit()
    flash('Expense removed.', 'info')
    return redirect(url_for('budget.view', eid=eid))
