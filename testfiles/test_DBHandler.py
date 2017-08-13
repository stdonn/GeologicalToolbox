# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from Resources.DBHandler import DBHandler, Base


class User(Base):
	__tablename__ = 'users'

	id = sq.Column(sq.INTEGER, sq.Sequence('user_id_seq'), primary_key=True)
	name = sq.Column(sq.TEXT(50), unique=True)
	password = sq.Column(sq.TEXT(20))
	addresses = relationship("Address", back_populates='user')

	def __repr__(self):
		return "<User[{}] name='{}': password='{}' - addresses: {})>"\
			.format(self.id, self.name, self.password, self.addresses)

	def __str__(self):
		return "[{}] name='{}': password='{}' - addresses: {}".format(self.id, self.name, self.password, self.addresses)


class Address(Base):
	__tablename__ = "addresses"

	id = sq.Column(sq.INTEGER, sq.Sequence('addresses_id_seq'), primary_key=True)
	email_address = sq.Column(sq.TEXT(50), nullable=False, unique=True)
	user_id = sq.Column(sq.ForeignKey('users.id'))
	user = relationship("User", back_populates="addresses")

	def __repr__(self):
		return "<[{}] Address(email_address='{}')>".format(self.id, self.email_address)

	def __str__(self):
		return "[{}] email_address={})>".format(self.id, self.email_address)


if __name__ == '__main__':
	# handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)
	handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)
	session = handler.getSession()

	Users = [
		{'name': 'Stephan', 'password': 'asdf'},
		{'name': 'Paul', 'password': 'dfsuih'},
		{'name': 'Melissa', 'password': 'sdfsdf'},
		{'name': 'Klaus', 'password': 'asdfslakdhjg32'}
	]
	users = [User(name=user['name'], password=user['password']) for user in Users]
	session.add_all(users)

	Addresses = [
		{'email_address': 'stephan.donndorf@googlemail.com', 'user': users[0]},
		{'email_address': 'stephan@donndorf.info', 'user': users[0]},
		{'email_address': 'klaus-donndorf@t-online.de', 'user': users[3]}
	]
	addresses = [Address(email_address=address['email_address'], user=address['user']) for address in Addresses]
	session.add_all(addresses)

	try:
		session.commit()
	except IntegrityError as e:
		print('Cannot commit changes, Integrity Error (double unique values?)')
		print(e)
		session.rollback()

	result = session.query(User).filter(User.name.in_(['Stephan', 'Klaus'])).all()
	for us in result:
		print(str(us))

	result = session.query(Address).all()
	for add in result:
		print(str(add))
