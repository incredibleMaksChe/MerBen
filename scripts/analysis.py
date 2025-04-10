import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import logging


def analyze_data(data_path='data/raw_data.csv', artifacts_dir='artifacts/'):
    try:
        os.makedirs(artifacts_dir, exist_ok=True)

        df = pd.read_csv(data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].astype(int)

        plt.figure(figsize=(12, 6))
        df.groupby(df['timestamp'].dt.date)['price'].mean().plot(
            title='Динамика средних цен на Mercedes W124',
            grid=True,
            marker='o'
        )
        plt.ylabel('Цена (руб)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{artifacts_dir}/price_dynamics.png')

        report = f"""
        ## Отчет мониторинга цен {datetime.now().date()}
        - **Всего объявлений**: {len(df)}
        - **Новых за сегодня**: {len(df[df['timestamp'].dt.date == datetime.now().date()])}
        - **Средняя цена**: {df['price'].mean():.0f} руб
        - **Минимальная цена**: {df['price'].min()} руб
        - **Максимальная цена**: {df['price'].max()} руб
        """
        with open(f'{artifacts_dir}/report.md', 'w') as f:
            f.write(report)

        logging.info("Артефакты успешно сгенерированы")

    except Exception as e:
        logging.error(f"Ошибка анализа: {str(e)}")
