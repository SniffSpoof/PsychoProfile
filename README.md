## CrewAI
Руководство для CrewAI
### Установить CrewAI 
```bash
pip install 'crewai[tools]'
```

### Создать проект
```bash
crewai create crew psycho
```
В ходе создания выбрать Gemini и вписать свой api_key

### Добавить путь до вашего диалога
В crew.py на 5 и 6 строчках: 
```python
read_file_tool = FileReadTool(file_path='enter your file path') #диалог
read_file_tool_profile = FileReadTool(file_path='enter your file path') #итоговый псих. портрет
```
заменить на свой. Тоже самое, для удобства, можно сделать в main.py

### Запуск
В директории psycho
```bash
crewai run
```
При "Enter the file name" вписывать без .txt
