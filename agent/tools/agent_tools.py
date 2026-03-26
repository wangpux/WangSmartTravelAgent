import json
from langchain.tools import tool
from utils.path_tool import get_abspath
from utils.logger_handler import logger
from rag.rag_service import rag_service


@tool
def guide_rag(query: str) -> str:
    """
    当你需要查询关于某个旅游目的地的非结构化信息时使用。
    包括目的地的文化背景、历史特色、著名景点描述、美食推荐及游玩细节。
    入参 query 应该是具体的查询词，如“大理有哪些人文特色？”。
    """
    logger.info(f"[Tool] 调用 RAG 检索: {query}")
    return rag_service.rag_summarize(query)

@tool
def weather_api(city: str) -> str:
    """
    获取指定城市的实时气候特征和穿衣建议。
    入参 city 必须是中文城市名称，如“北京”、“三亚”。
    """
    weather_mock = {
        "北京": "晴，15-22°C，气候干燥，建议穿薄外套。",
        "三亚": "多云转晴，25-30°C，紫外线强，建议防晒。",
        "哈尔滨": "小雪，-15至-5°C，严寒，需准备羽绒服。",
        "成都": "阴，18-23°C，微湿，建议穿着舒适。"
    }
    res = weather_mock.get(city, f"{city}当前气候适中，平均气温20°C左右。")
    logger.info(f"[Tool] 获取{city}天气: {res}")
    return res

@tool
def booking_db_query(city: str) -> str:
    """
    查询特定城市的结构化旅游数据，包括酒店均价、门票总额和城市标签。
    当需要核实某个城市的消费水平或判断其属性（如是否为“避暑”或“古风”）时使用。
    """
    try:
        with open(get_abspath("data/city_data.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
        info = data.get(city)
        if info:
            return f"城市：{city}\n标签：{info['tags']}\n酒店均价：{info['hotel_avg']}元/晚\n门票总额：{info['ticket_total']}元"
        return f"数据库中暂未收录{city}的数据。"
    except Exception as e:
        return f"查询数据库失败: {e}"

@tool
def calculate_travel_cost(city: str, days: int) -> str:
    """
    计算特定城市在指定天数内的预估总预算（包含酒店、餐饮及门票）。
    当用户询问“去XX玩几天要多少钱”或需要核实预算是否足够时调用。
    入参 city 必须是中文城市名；days 必须是整数天数。
    """
    logger.info(f"[Tool] 正在计算 {city} {days} 天的行程预算...")

    # 1. 获取数据库绝对路径并加载
    try:
        with open(get_abspath("data/city_data.json"), 'r', encoding='utf-8') as f:
            city_data = json.load(f)

        info = city_data.get(city)
        if not info:
            return f"抱歉，数据库中暂未收录 {city} 的消费数据，无法计算精确预算。"

        # 2. 提取各项单价
        hotel_price = info.get("hotel_avg", 0)
        food_price = info.get("daily_food_avg", 150)  # 若无数据则取默认值 150
        ticket_price = info.get("ticket_total", 0)

        # 3. 执行核心逻辑计算
        # 公式：(酒店 + 餐饮) * 天数 + 门票总额
        stay_cost = (hotel_price + food_price) * days
        total_cost = stay_cost + ticket_price

        # 4. 构造详细的返回字符串，方便 Agent 进行后续推理
        result = (
            f"--- {city} {days}天预算审计清单 ---\n"
            f"1. 住宿与餐饮预估：{stay_cost} 元 ({hotel_price + food_price}元/天)\n"
            f"2. 景点门票总计：{ticket_price} 元\n"
            f"3. 总计预估开支：{total_cost} 元\n"
            f"提示：该计算基于当前城市平均消费水平，不含往返大交通费用。"
        )

        logger.info(f"[Tool] 预算计算完成，总额: {total_cost}")
        return result

    except Exception as e:
        logger.error(f"计算预算时发生程序错误: {e}")
        return f"预算计算工具暂时不可用，错误原因: {str(e)}"


@tool
def generate_report_signal(final_summary: str) -> str:
    """
    当且仅当你已经通过其他工具(weather_api, guide_rag等)搜集齐了所有必要的行程信息，
    且准备好为用户生成最终的【正式报告/行程单】时，最后调用此工具。
    入参 final_summary 应该是你对本次行程核心要素（地点、天数、预算、天气亮点）的简要汇总。
    """
    return "报告生成协议已激活，正在切换专家排版模式..."


# 导出工具列表给 Agent 使用
travel_tools = [guide_rag, weather_api, booking_db_query, calculate_travel_cost, generate_report_signal]