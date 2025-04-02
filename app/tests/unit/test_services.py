from typing import Iterable
import datetime
import pytest
from ...services import Services
from ...database import MyEngine
from ...database import Payment, Tax, User


class TestServicesPositive:

    def test_check_taxes(self, capsys, mock_engine, auth_mock):
        auth = auth_mock
        assert auth.user != None
        assert 'water' in [tax.taxname for tax in auth.user.taxes]
        services: Services = Services(auth, mock_engine)
        capsys.readouterr()
        result: dict[int, Tax] = services.check_taxes(simple=True)
        assert result != {}
        captured_output = capsys.readouterr()
        assert 'water' in captured_output.out.strip()
        assert '0' in captured_output.out.strip()
        assert isinstance(result, dict) == True

    def test_check_taxes_simple(self, capsys, mock_engine, auth_mock):
        auth = auth_mock 
        assert auth.user != None
        services: Services = Services(auth, mock_engine)

        result: dict[int, Tax] = services.check_taxes(simple=True)
        captured_output = capsys.readouterr()
        assert 'water' in captured_output.out.strip()
        assert '0' in captured_output.out.strip()
        assert isinstance(result, dict) == True

    def test_pay_taxes(self, capsys, mock_engine, auth_mock):
        services: Services = Services(auth_mock, mock_engine)

        inputs: Iterable = iter(['y', '100'])

        services.pay_taxes('water', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        assert 'paid successfully' in captured_output.out.strip()

    def test_pay_unexisting_taxes(self, capsys, mock_engine_no_query, auth_mock):
        services: Services = Services(auth_mock, mock_engine_no_query)

        inputs: Iterable = iter(['y', '100'])

        services.pay_taxes('eter', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        assert ' not found, attempting to add tax' in captured_output.out.strip()
        assert 'paid successfully' in captured_output.out.strip()

    def test_cancel_payment(self, capsys, ex_user, mock_engine, auth_mock) -> None:
        services: Services = Services(auth_mock, mock_engine)
        engine: MyEngine = mock_engine

        inputs: Iterable = iter(['n'] * 2)

        services.pay_taxes('eter', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        assert 'Aborted' in captured_output.out.strip()
        assert 'paid successfully' not in captured_output.out.strip()

        services.pay_taxes('water', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        assert 'Aborted' in captured_output.out.strip()
        assert 'paid successfully' not in captured_output.out.strip()

    def test_view_payments(self, mock_engine, auth_mock, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)

        inputs: Iterable = iter([''])

        services.view_payments('water', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'not found' not in coe

    def test_edit_payment_cancel(self, mock_engine, auth_mock, capsys, ex_user) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter(['y', '100', 'q'])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()

        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe

    def test_edit_payment_delete_payment(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter(['y', '100', '2', 'Y'])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()

        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' in coe
        assert 'Canceled' not in coe

    def test_edit_payment_delete_payment_cancel(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter(['y', '100', '2', 'n'])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()

        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' in coe

    def test_payment_edit_details(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        school_tax_id: int = next(tax for tax in services.user.taxes if tax.taxname == 'school').id
        inputs: Iterable = iter([
            'y', '100', '1', '1', '28', 'January', '1999', '2', '123', '3', str(school_tax_id), 'q', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe

    def test_payment_edit_details_delete_cancel(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '4', 'n', 'q', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Deleted successfully' not in coe
        assert 'Canceled' in coe

    def test_payment_edit_details_delete(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '4', 'Y', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Deleted successfully' in coe
        assert 'Canceled' not in coe

    def test_payment_edit_details_invalid_choice(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '8', '28', 'January', '1999','a', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe
        assert 'Abandoned changes' in coe

    def test_payment_edit_details_abandon(self, mock_engine, auth_mock, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        school_tax_id: int = next(tax for tax in services.user.taxes if tax.taxname == 'school').id
        inputs: Iterable = iter([
            'y', '100', '1', '1', '28', 'January', '1999', '2', '123', '3', str(school_tax_id), 'a', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe
        assert 'Abandoned changes' in coe

    def test_delete_tax(self, mock_engine_with_user, auth_mock, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        inputs: Iterable = iter(['Y'])
        assert user is not None
        taxname: str = user.taxes[0].taxname
        services.delete_tax(taxname=taxname, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()
        assert 'Deleted successfully' in captured_output

    def test_delete_tax_canceled(self, ex_user, mock_engine_with_user, auth_mock, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        inputs: Iterable = iter(['n'])
        assert user is not None
        taxname: str = user.taxes[0].taxname
        services.delete_tax(taxname=taxname, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()
        assert 'Canceled' in captured_output

    def test_delete_tax_by_id(self, auth_mock, mock_engine_with_user, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        inputs: Iterable = iter(['Y'])
        assert user is not None
        tax_id: int = user.taxes[0].id
        services.delete_tax(tax_id=tax_id, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()
        assert 'Deleted successfully' in captured_output

    def test_add_tax(self, auth_mock, mock_engine_with_user, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        assert user is not None
        taxname: str = 'testtax'
        inputs: Iterable = iter(['y'])
        services.add_tax(taxname=taxname, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()
        user_taxes: list[Tax] = user.taxes

        assert 'added successfully' in captured_output

    def test_add_tax_and_cancel(self, auth_mock, mock_engine_with_user, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        assert user is not None
        taxname: str = 'testtax'
        inputs: Iterable = iter(['n'])
        services.add_tax(taxname=taxname, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()

        assert 'Canceled' in captured_output

    def test_edit_tax(self, auth_mock, mock_engine_with_user, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        assert user is not None
        taxname: str = user.taxes[0].taxname
        inputs: Iterable = iter(['new_name', 'y'])
        services.edit_tax(taxname=taxname, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()

        assert 'edited successfully' in captured_output

    def test_edit_tax_by_id(self, auth_mock, mock_engine_with_user, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_with_user)
        user: User | None = mock_engine_with_user.get_user(username=ex_user[0])
        assert user is not None
        tax_id: int = user.taxes[0].id
        taxname: str = 'testtax'
        inputs: Iterable = iter([taxname, 'y'])
        services.edit_tax(tax_id=tax_id, input_method=lambda _: next(inputs))
        captured_output: str = capsys.readouterr().out.strip()

        assert 'edited successfully' in captured_output


class TestServicesNegative:
    def test_changing_unchangable_attributes_auth(self, auth_mock, mock_engine) -> None:
        services: Services = Services(auth_mock, mock_engine)

        with pytest.raises(AttributeError, match='This attribute cannot be changed directly'):
            services.auth = auth_mock

    def test_changing_unchangable_attributes_engine(self, mock_engine, auth_mock, no_session) -> None:
        services: Services = Services(auth_mock, mock_engine)

        with pytest.raises(AttributeError, match='This attribute cannot be changed directly'):
            services.engine = no_session

    # def test_check_taxes_not_logged_in(self, mock_engine, capsys, auth_mock_no_user, monkeypatch) -> None:
    #     username: str = 'tctnli11'
    #     password: str = 'StrongPass!'
    #     user = mock_engine.create_user(username=username, password=password)
    #     auth = auth_mock_no_user
    #     services: Services = Services(auth=auth, engine=mock_engine)
    #
    #     inputs: Iterable = iter([username, password])
    #     monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    #     services.check_taxes()
    #     captured_output = capsys.readouterr()
    #     coe: str = captured_output.out.strip()
    #     assert 'You must log in to use services!' in coe
    #     assert 'Tax' in coe
    #     assert 'Is paid?' in coe
    #
    # def test_check_taxes_not_logged_in_second_try(self, monkeypatch, mock_engine, capsys, auth_mock_no_user) -> None:
    #     username: str = 'tctnli11'
    #     password: str = 'StrongPass!'
    #     auth = auth_mock_no_user
    #     services: Services = Services(auth=auth, engine=mock_engine)
    #
    #     inputs: Iterable = iter(['wrongusername', 'wrongpass', username, password])
    #     monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    #     services.check_taxes()
    #     captured_output = capsys.readouterr()
    #     coe: str = captured_output.out.strip()
    #     assert 'You must log in to use services!' in coe
    #     assert 'Tax' in coe
    #     assert 'Is paid?' in coe
    #
    def test_pay_taxes_no_float(self, mock_engine, auth_mock, ex_user):
        services: Services = Services(auth_mock, mock_engine)
        engine: MyEngine = mock_engine

        inputs: Iterable = iter(['y', 'Pszemek'])
        with pytest.raises(ValueError, match='could not convert'):
            services.pay_taxes('water', input_method=lambda _: next(inputs))

        user: User | None = engine.session.query(User).filter_by(name=ex_user[0]).first()
        assert user != None

    def test_view_payments_while_no_taxes(self, auth_mock_user_no_taxes, capsys, mock_engine_no_query) -> None:
        services: Services = Services(auth_mock_user_no_taxes, mock_engine_no_query)

        services.view_payments('insanenamefortax')
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'not found' in coe

    def test_view_payments_while_no_taxes2(self, auth_mock_user_no_taxes, capsys, mock_engine_no_query) -> None:
        services: Services = Services(auth_mock_user_no_taxes, mock_engine_no_query)

        result: None = services.view_payments('water')  #  basic tax, should exist normally
        assert result is None
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'not found' in coe

    def test_view_payments_unknown_choice(self, mock_engine, auth_mock, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)

        inputs: Iterable = iter(['Spain'])

        services.view_payments('water', input_method=lambda _: next(inputs))

        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'not found' not in coe
        assert 'Unknown choice' in coe
        

    def test_view_payments_not_exsiting_tax(self, mock_engine_no_query, auth_mock, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_no_query)

        services.view_payments('Spain')

        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'ID' not in coe
        assert 'Price' not in coe
        assert 'not found' in coe
        assert 'Unknown choice' not in coe

    def test_edit_payment_cancel_invalid_option(self, ex_user, auth_mock, mock_engine, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter(['y', '100', 'whatisthis', 'quit'])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id


        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()

        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Invalid option' in coe

    def test_payment_edit_details_value_error(self, mock_engine, auth_mock, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '1'] + ['lol', 'January', '1999']+ ['1', '28', 'nonmonth', '1999'] +
            ['1', '28', '1', 'myyear'] + ['q', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe
        assert 'invalid literal for int() with base 10: \'lol\'' in coe
        assert 'This is not a month: nonmonth' in coe.split('\n')
        assert 'invalid literal for int() with base 10: \'myyear\''in coe

    def test_payment_edit_details_second_option_value_error(self, mock_engine, auth_mock, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '2'] + ['lol']+ ['2', '11p'] +
            ['q', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        payment_id: int = 11  # just to test output

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe
        assert 'invalid literal for int() with base 10: \'lol\'' in coe
        assert 'invalid literal for int() with base 10: \'11p\''in coe


    def test_payment_edit_details_third_option_value_error(self, auth_mock, mock_engine, ex_user, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine)
        inputs: Iterable = iter([
            'y', '100', '1', '3'] + ['lol']+ ['3', '11p'] + ['3', '1111111111111111'] +
            ['q', 'q'
        ])
        services.pay_taxes('water', input_method=lambda _: next(inputs))
        user_id: int = mock_engine.session.query(User).filter_by(name=ex_user[0]).first().id
        payment_id: int = mock_engine.session.query(Payment).filter_by(users_id=user_id).first().id

        services.edit_payment(payment_id, input_method=lambda _: next(inputs))
        captured_output = capsys.readouterr()
        coe: str = captured_output.out.strip()
        assert 'Selected payment is not found' not in coe
        assert 'ID' in coe
        assert 'Price' in coe
        assert 'Removed successfully' not in coe
        assert 'Canceled' not in coe
        assert 'Error occured:\ninvalid literal for int() with base 10: \'lol\'' in coe
        assert 'Error occured:\ninvalid literal for int() with base 10: \'11p\'' in coe
        assert 'Id out of range' in coe

    def test_delete_not_exisitng_tax(self, auth_mock, mock_engine_no_query) -> None:
        services: Services = Services(auth_mock, mock_engine_no_query)
        inputs: Iterable = iter(['Y'])
        taxname: str = 'this is not valid name'
        with pytest.raises(KeyError, match='Tax doesn\'t exist'):
            services.delete_tax(taxname=taxname, input_method=lambda _: next(inputs))

    def test_delete_not_existing_tax_by_id(self, auth_mock, mock_engine_no_query) -> None:
        services: Services = Services(auth_mock, mock_engine_no_query)
        inputs: Iterable = iter(['Y'])
        tax_id: int = -1
        with pytest.raises(KeyError, match="Tax doesn't exist"):
            services.delete_tax(tax_id=tax_id, input_method=lambda _: next(inputs))

    def test_edit_not_existent_tax(self, auth_mock, mock_engine_no_query) -> None:
        services: Services = Services(auth_mock, mock_engine_no_query)
        taxname: str = 'this is not valid tax name'
        with pytest.raises(KeyError, match="Tax doesn't exist"):
            services.edit_tax(taxname=taxname)

    def test_edit_non_existent_tax_by_id(self, auth_mock, mock_engine_no_query, capsys) -> None:
        services: Services = Services(auth_mock, mock_engine_no_query)
        tax_id: int = -1
        with pytest.raises(KeyError, match="Tax doesn't exist"):
            services.edit_tax(tax_id=tax_id)
        captured_output: str = capsys.readouterr().out.strip()

        assert 'edited successfully' not in captured_output
