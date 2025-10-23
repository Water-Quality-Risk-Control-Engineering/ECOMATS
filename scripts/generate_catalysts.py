#!/usr/bin/env python3
"""
生成10种催化PMS活化的催化剂材料的简化脚本
"""

def generate_catalysts():
    """生成10种催化PMS活化的催化剂材料"""
    
    catalysts = [
        {
            "name": "Co3O4纳米片",
            "structure": "具有暴露{111}晶面的Co3O4纳米片，片层厚度约5-10 nm",
            "synthesis": [
                "1. 将Co(NO3)2·6H2O (291 mg, 1 mmol)溶解在50 mL乙二醇中",
                "2. 加入10 mL去离子水，搅拌30分钟",
                "3. 将溶液转移至100 mL聚四氟乙烯内衬反应釜中",
                "4. 在200°C下反应12小时",
                "5. 自然冷却至室温，离心收集产物",
                "6. 用乙醇洗涤3次，在60°C下真空干燥6小时"
            ]
        },
        {
            "name": "Fe2O3纳米棒",
            "structure": "α-Fe2O3纳米棒，长度约1-2 μm，直径约50-100 nm",
            "synthesis": [
                "1. 将FeCl3·6H2O (270 mg, 1 mmol)和尿素(300 mg, 5 mmol)溶解在40 mL去离子水中",
                "2. 加入5 mL乙二醇，搅拌1小时",
                "3. 转移至80 mL水热反应釜中",
                "4. 在180°C下反应24小时",
                "5. 冷却后离心分离，用去离子水洗涤",
                "6. 在80°C下干燥12小时"
            ]
        },
        {
            "name": "MnO2纳米花",
            "structure": "δ-MnO2纳米花结构，由超薄纳米片自组装而成",
            "synthesis": [
                "1. 将KMnO4 (158 mg, 1 mmol)溶解在30 mL去离子水中",
                "2. 缓慢加入HCl (37%, 0.5 mL)并搅拌",
                "3. 在90°C下反应6小时",
                "4. 离心收集沉淀物，用去离子水洗涤至中性",
                "5. 在70°C下干燥8小时"
            ]
        },
        {
            "name": "Cu2O立方体",
            "structure": "Cu2O微米立方体，边长约2-5 μm",
            "synthesis": [
                "1. 将CuSO4·5H2O (250 mg, 1 mmol)和柠檬酸钠(147 mg, 0.5 mmol)溶解在50 mL去离子水中",
                "2. 加入20 mL 1 M NaOH溶液",
                "3. 在95°C下搅拌反应3小时",
                "4. 离心收集产物，用乙醇洗涤",
                "5. 在60°C下干燥10小时"
            ]
        },
        {
            "name": "Ni(OH)2纳米片",
            "structure": "β-Ni(OH)2纳米片，厚度约2-5 nm",
            "synthesis": [
                "1. 将Ni(NO3)2·6H2O (291 mg, 1 mmol)和尿素(600 mg, 10 mmol)溶解在60 mL去离子水中",
                "2. 转移至100 mL反应釜中",
                "3. 在120°C下反应20小时",
                "4. 冷却后离心，用去离子水洗涤",
                "5. 在70°C下干燥12小时"
            ]
        },
        {
            "name": "ZnCo2O4尖晶石",
            "structure": "ZnCo2O4尖晶石结构，粒径约20-50 nm",
            "synthesis": [
                "1. 将Zn(NO3)2·6H2O (297 mg, 1 mmol)和Co(NO3)2·6H2O (582 mg, 2 mmol)溶解在40 mL乙二醇中",
                "2. 加入2 g柠檬酸作为络合剂",
                "3. 在160°C下溶剂热反应15小时",
                "4. 离心收集产物，用乙醇洗涤",
                "5. 在400°C下煅烧3小时"
            ]
        },
        {
            "name": "FeCo2O4纳米线",
            "structure": "FeCo2O4纳米线，长度约5-10 μm，直径约30-50 nm",
            "synthesis": [
                "1. 将Fe(NO3)3·9H2O (404 mg, 1 mmol)和Co(NO3)2·6H2O (582 mg, 2 mmol)溶解在50 mL去离子水中",
                "2. 加入15 mL 10 M NaOH溶液",
                "3. 在100°C下水热反应18小时",
                "4. 离心分离，用去离子水洗涤",
                "5. 在350°C下煅烧2小时"
            ]
        },
        {
            "name": "CeO2纳米立方体",
            "structure": "CeO2纳米立方体，边长约50-100 nm",
            "synthesis": [
                "1. 将Ce(NO3)3·6H2O (434 mg, 1 mmol)溶解在30 mL乙二醇中",
                "2. 加入10 mL去离子水和5 mL氨水",
                "3. 在140°C下反应8小时",
                "4. 离心收集产物，用乙醇洗涤",
                "5. 在500°C下煅烧4小时"
            ]
        },
        {
            "name": "MoS2纳米片",
            "structure": "少层MoS2纳米片，厚度约1-3 nm",
            "synthesis": [
                "1. 将Na2MoO4·2H2O (242 mg, 1 mmol)和硫脲(76 mg, 1 mmol)溶解在40 mL去离子水中",
                "2. 转移至80 mL反应釜中",
                "3. 在220°C下反应24小时",
                "4. 冷却后离心，用去离子水和乙醇洗涤",
                "5. 在80°C下干燥12小时"
            ]
        },
        {
            "name": "Bi2O3微米球",
            "structure": "β-Bi2O3微米球，直径约1-3 μm",
            "synthesis": [
                "1. 将Bi(NO3)3·5H2O (485 mg, 1 mmol)溶解在20 mL乙二醇中",
                "2. 加入5 mL去离子水和2 mL氨水",
                "3. 在160°C下溶剂热反应12小时",
                "4. 离心分离，用乙醇洗涤",
                "5. 在300°C下煅烧3小时"
            ]
        }
    ]
    
    return catalysts

def print_catalysts(catalysts):
    """打印催化剂信息"""
    print("10种催化PMS活化的催化剂材料")
    print("=" * 50)
    
    for i, catalyst in enumerate(catalysts, 1):
        print(f"\n{i}. {catalyst['name']}")
        print(f"   结构: {catalyst['structure']}")
        print("   合成方法:")
        for step in catalyst['synthesis']:
            print(f"     {step}")

if __name__ == "__main__":
    catalysts = generate_catalysts()
    print_catalysts(catalysts)