# -*- coding: UTF-8 -*-

import sqlalchemy as sq

from Resources.DBHandler import DBHandler, Base


class User(Base):
	__tablename__ = 'users'

	id = sq.Column(sq.INTEGER, sq.Sequence('user_id_seq'), primary_key=True)
	name = sq.Column(sq.TEXT(50))
	password = sq.Column(sq.TEXT(20))

	def __repr__(self):
		return "<User[{}] name='{}': password='{}')>".format(self.id, self.name, self.password)

	def __str__(self):
		return "[{}] name='{}': password='{}'".format(self.id, self.name, self.password)


Users = [
	{'name': 'Stephan', 'password': 'asdf'},
	{'name': 'Paul', 'password': 'dfsuih'},
	{'name': 'Melissa', 'password': 'sdfsdf'},
	{'name': 'Klaus', 'password': 'asdfslakdhjg32'}
]

if __name__ == '__main__':
	handler = DBHandler(debug=True)
	session = handler.getSession()
	users = [User(name=user['name'], password=user['password']) for user in Users]
	session.add_all(users)
	session.commit()

	result = session.query(User).filter(User.name.in_(['Stephan', 'Klaus'])).all()
	for us in result:
		print(str(us))


