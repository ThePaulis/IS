from xml.dom import minidom

# Carrega o ficheiro xml e da parse ao mesmo
try:
    xml_doc = minidom.parse('sample.xml')
except Exception as e:
    print(f"Error parsing XML: {e}")
    exit()

# Da print ao nome da tag raiz do ficheiro xml
root = xml_doc.documentElement
print(f"Root tag: {root.tagName}")

# Faz display da informações de todos os empregados 
employees = root.getElementsByTagName('employee')
for employee in employees:
    employee_id = employee.getAttribute('id')
    name = employee.getElementsByTagName('name')[0].firstChild.data
    position = employee.getElementsByTagName('position')[0].firstChild.data
    salary = employee.getElementsByTagName('salary')[0].firstChild.data
    
    print(f"Employee ID: {employee_id}, Name: {name}, Position: {position}, Salary: {salary}")

# Regista um novo empregado
new_employee = xml_doc.createElement('employee')
new_employee.setAttribute('id', '103')

name = xml_doc.createElement('name')
name.appendChild(xml_doc.createTextNode('Alice Johnson'))
new_employee.appendChild(name)

position = xml_doc.createElement('position')
position.appendChild(xml_doc.createTextNode('Manager'))
new_employee.appendChild(position)

salary = xml_doc.createElement('salary')
salary.appendChild(xml_doc.createTextNode('70000'))
new_employee.appendChild(salary)

root.appendChild(new_employee)

# Salva as mudanças em um novo ficheiro
with open('updated_sample.xml', 'w') as file:
    xml_doc.writexml(file, indent="  ", addindent="  ", newl="\n")
