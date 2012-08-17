#!python3
from urllib.request import urlopen
from bs4 import BeautifulSoup as parse
import re
from xml.dom.minidom import Document

day_regex = re.compile('(?P<date>\d{2}\.\d{2}\.\d{4})')
extra_regex = re.compile('\((?P<number>\d+)\)')
legend_regex = re.compile('(?P<number>\d+)\) (?P<value>\w+(\s+\w+)*)')
def rolesGenerator():
	yield 'student'
	yield 'employee'
	while True:
		yield 'other'


def parse_url(url):
	content = urlopen(url).read()
	document = parse(content)
	legends = document.find_all('div', {'class':'legende'})
	if len(legends) > 0:
		extraLegend = { int(v[0]): v[1] for v in reversed(legend_regex.findall(legends[0].text)) }
	else:
		extraLegend = {}
	output = Document()
	openmensa = output.createElement('openmensa')
	openmensa.setAttribute('version', '2.0')
	openmensa.setAttribute('xmlns',"http://openmensa.org/open-mensa-v2")
	openmensa.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
	openmensa.setAttribute('xsi:schemaLocation', "http://openmensa.org/open-mensa-v2 http://openmensa.org/open-mensa-v2.xsd")
	output.appendChild(openmensa)
	canteen = output.createElement('canteen')
	openmensa.appendChild(canteen)
	for day_td in document.find_all('td', text = day_regex):
		date = day_regex.search(day_td.string).group('date')
		table = None
		for element in day_td.parents:
			if element.name == 'table':
				table = element
				break
		if not table: continue
		day = output.createElement('day')
		day.setAttribute('date', '{}-{}-{}'.format(date[6:10], date[3:5], date[0:2]))
		category = output.createElement('category')
		category.setAttribute('name', 'Hauptgerichte')
		for tr in table.tbody.find_all('tr'):
			if len(tr) != 3 : continue # no meal
			strings = list(tr.contents[0].strings)
			meal = output.createElement('meal')
			name = output.createElement('name')
			name.appendChild(output.createTextNode(strings[0]))
			meal.appendChild(name)
			# notes:
			notes = []
			for img in tr.contents[1].find_all('img'):
				notes.append(img['alt'].replace('Symbol', '').strip())
			for extra in list(set(map(lambda v: int(v), extra_regex.findall(tr.text)))):
				if extra in extraLegend:
					notes.append(extraLegend[extra])
			for noteText in notes:
				note = output.createElement('note')
				note.appendChild(output.createTextNode(noteText))
				meal.appendChild(note)
			prices = {}
			for k, v in enumerate(strings[-1].split('|')):
				prices[roles[k]] = v.strip().replace(',', '.')	
				price = output.createElement('price')
				price.setAttribute('role', roles[k])
				price.appendChild(output.createTextNode(v.strip().replace(',', '.')))
				meal.appendChild(price)
			category.appendChild(meal)
		day.appendChild(category)
		canteen.appendChild(day)
	return '<?xml version="1.0" encoding="UTF-8"?>\n' + openmensa.toprettyxml(indent='  ')
