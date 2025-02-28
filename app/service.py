from sqlalchemy.orm import scoped_session
from .database.models import User, Payment, Tax
from .utils import simple_logs, taxes, update



    
def view_payments(user: User, tax: str, session: scoped_session) -> None:
    selected_tax: Tax | None = session.query(Tax).filter_by(taxname=tax, user_id=user.id).first()
    if not selected_tax:
        print(f'{tax} not found')
        simple_logs(f'{tax} not found', log_file=['taxes.log'])
        return None
    payments: list[Payment] = session.query(Payment).filter_by(users_id=user.id, taxes_id=selected_tax.id).all()
    print('')
    print('ID  |  Price  |  Date')
    for payment in payments:
        print(f'{payment.id})\t{payment.price}\t{payment.date}')
    print('')
    return


def edit_payment(user: User, session: scoped_session) -> None:
    while True:
        try:
            py_id: int = int(input('Enter payment id (q to quit): '))
        except ValueError:
            print('Exiting')
            return
        payment: Payment | None = session.query(Payment).filter_by(id=py_id, users_id=user.id).first()
        if not payment:
            print('Payment not found')
            simple_logs(f'Payment with id {py_id} of user {user.name} not found', log_file=['taxes.log'])
            return
        
        while True:
            print(payment)
            message: str = '''
                1. Edit price
                2. Edit date
                3. Delete payment
                q. Quit and save
                '''
            choice: str = input(message).lower()
            match choice:
                case '1':
                    price: float = float(input('Enter new price: '))
                    payment.price = price
                case '2':
                    # date: str = input('Enter new date (dd-mm-YYYY): ')
                    day: str = input('Enter day: ')
                    month: str = input('Enter month: ')
                    year: str = input('Enter year: ')
                    payment.date = day + '-' + month + '-' + year
                case '3':
                    session.delete(payment)
                    session.commit()
                    update()
                    break
                case 'q':
                    session.add(payment)
                    session.commit()
                    break
                case _:
                    print('Invalid choice')
