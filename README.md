# Mercedes W124 мониторинг

Проект для непрерывного мониторинга цен на Mercedes-Benz W124 (купе/универсал) с автоматическим скрапингом данных и анализом рынка.


### Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/incredibleMaksChe/MerBen.git
cd MerBen
```
2. Установить зависимости:
```bash
pip install -r requirements.txt
```
### Запуск скрапера:
```bash
python src/scraper.py
```
### Запуск через prefect

1. Запустить сервер Prefect:
```bash
prefect server start
```
2. Создать деплоймент:
```bash
prefect deployment create flows/prefect_flow.py
```
3. Запустить агент:
```bash
prefect agent start -q default
```
### После каждого запуска генерируются:

Артефакты каждого запуска сохраняются в папку `artifacts`:
src/artifacts
- `price_dynamics.png` - график изменения средних цен
- `report.md` - сводный отчет по данным

Сырые данные: src/data/raw_data.csv