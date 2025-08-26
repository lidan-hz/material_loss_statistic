import os

from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# 中文支持（避免乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

@app.route("/", methods=["GET", "POST"])
def index():
    result_html = None
    # 在 index() 里加上默认值
    today = datetime.today().date()
    default_start = today - timedelta(days=6)
    default_end = today

    # 读取 Excel
    df = pd.read_excel("损.xlsx")
    df['日期'] = pd.to_datetime(df['日期'])

    if request.method == "POST":
        # 获取用户输入的起止日期
        start_date = pd.to_datetime(request.form["start"])
        end_date = pd.to_datetime(request.form["end"])

        # 筛选区间内数据
        mask = (df['日期'] >= start_date) & (df['日期'] <= end_date)
        selected_df = df.loc[mask]
        sum_selected = selected_df.drop(columns=['日期']).sum()

        # 生成表格 HTML
        result_html = sum_selected.reset_index().rename(
            columns={"index": "物料", 0: "损耗总和"}
        ).to_html(index=False, classes="table table-bordered table-striped")

        # 绘制美观的图表
        plt.figure(figsize=(8, 6))
        bars = plt.bar(sum_selected.index, sum_selected.values, color="#4a90e2")
        plt.title("物料损耗统计", fontsize=16)
        plt.xlabel("物料")
        plt.ylabel("损耗总和")
        plt.grid(axis="y", linestyle="--", alpha=0.6)

        # 给柱子加标签
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                     f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        # plt.savefig("static/chart.png")
        # 如果 start_date / end_date 是 datetime 类型

        filename = f"static/{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')} 损耗.png"
        plt.savefig(filename)
        plt.close()

    else:
        start_date = default_start
        end_date = default_end
        filename=f"static/chart.png"

    return render_template("index.html",
                           result=result_html,
                           start_date=start_date.strftime("%Y-%m-%d"),
                           end_date=end_date.strftime("%Y-%m-%d"),
                           chart_file=filename,
                           cache_bust=str(time.time())  # ✅ 传时间戳给模板
                           )


if __name__ == "__main__":
    app.run(debug=True)
