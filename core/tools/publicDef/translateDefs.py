from enum import StrEnum

class LangEnum(StrEnum):
    ZH_CN = 'zh_cn'
    EN_US = 'en_us'

# 翻译字段名称
def tra(item: str) -> str:
    translateDict = {
        "author": "开发责任人",
        "no": "序号",
        "e2e": "E2E",
        "description": "描述",
        "title": "标题",
        "detail": "详细信息",
        "background": "背景",
        "changeType": "改动类型",
        "changeCode": "改动代码",
        "transferToTest": "是否澄清",
        "tester": "测试部接口人",
        "affectedProd": "涉及产品",
        "affectedFields": "周边影响",
        "selfTestReport": "自测报告",
        "testSuggestion" :"测试建议",
        "hexSha": "哈希",
        "branch": "分支",
    }
    return translateDict.get(item, '')