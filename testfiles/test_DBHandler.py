import sqlalchemy as sq

from DBHandler import DBHandler


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
	users = [User(name=user['name'], password=user['password']) for user in Users]
