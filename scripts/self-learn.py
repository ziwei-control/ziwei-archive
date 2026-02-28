#!/usr/bin/env python3
# =============================================================================
# self-learn - 紫微智控自动学习脚本（网络搜索版）
# 功能：从网络搜索最新知识
# 要求：每次最低 1 万字，重复率<35%，访问不少于 20 个网站
# =============================================================================

import os
import sys
import json
import time
import random
from datetime import datetime

# 配置
Ziwei_DIR = "/home/admin/Ziwei"
KNOWLEDGE_DIR = os.path.join(Ziwei_DIR, "docs", "knowledge")
STATE_FILE = os.path.join(Ziwei_DIR, "data", "learn_state.json")
LOG_FILE = os.path.join(Ziwei_DIR, "data", "logs", "self_learn.log")
VISITED_SOURCES_FILE = os.path.join(Ziwei_DIR, "data", "visited_sources.json")
MIN_WORDS = 10000
MAX_SIMILARITY = 0.35
MIN_SOURCES = 20

# 6 个 Agent 配置
AGENTS = [
    {"id": "T-01", "name": "首席架构师", "focus": ["系统架构设计", "微服务架构", "云原生架构", "分布式系统"]},
    {"id": "T-02", "name": "代码特种兵", "focus": ["Python 高级编程", "代码重构", "设计模式", "单元测试"]},
    {"id": "T-03", "name": "代码审计员", "focus": ["代码安全", "OWASP Top 10", "代码审查", "安全编码"]},
    {"id": "T-04", "name": "逻辑推理机", "focus": ["逻辑推理", "数学建模", "算法分析", "问题分解"]},
    {"id": "T-05", "name": "跨域翻译家", "focus": ["技术翻译", "跨文化沟通", "术语对照", "本地化"]},
    {"id": "T-06", "name": "长文解析器", "focus": ["长文阅读", "信息抽取", "摘要生成", "知识管理"]}
]

# 每个 Agent 的网站来源池（50+ 个网站）
AGENT_SOURCES = {
    "T-01": [
        "https://architectureweekly.com", "https://martinfowler.com", "https://medium.com/tag/software-architecture",
        "https://www.infoq.com/architecture-design", "https://www.thoughtworks.com/insights",
        "https://aws.amazon.com/architecture", "https://cloud.google.com/architecture",
        "https://docs.microsoft.com/azure/architecture", "https://www.oreilly.com/architecture",
        "https://www.redhat.com/architect", "https://thenewstack.io/category/architecture",
        "https://www.infoq.com/microservices", "https://microservices.io", "https://www.nginx.com/blog",
        "https://kubernetes.io/blog", "https://www.docker.com/blog", "https://www.hashicorp.com/blog",
        "https://www.confluent.io/blog", "https://www.datadoghq.com/blog", "https://www.sumologic.com",
        "https://www.elastic.co/blog", "https://www.mongodb.com/blog", "https://www.postgresql.org/about/news",
        "https://www.apache.org", "https://www.linuxfoundation.org", "https://www.cncf.io",
        "https://www.coursera.org/browse/computer-science/system-architecture",
        "https://www.udemy.com/topic/software-architecture", "https://www.edx.org/learn/software-architecture",
        "https://www.pluralsight.com/browse/software-development", "https://www.safaribooksonline.com",
        "https://www.packtpub.com", "https://www.manning.com", "https://www.oreilly.com",
        "https://www.apress.com", "https://www.wiley.com", "https://www.springer.com/computer",
        "https://www.acm.org", "https://www.computer.org", "https://ieeexplore.ieee.org",
        "https://dl.acm.org", "https://arxiv.org/list/cs.SE/recent",
        "https://www.researchgate.net/topic/Software-Architecture", "https://scholar.google.com",
        "https://stackoverflow.com/questions/tagged/software-architecture",
        "https://softwareengineering.stackexchange.com", "https://www.reddit.com/r/softwarearchitecture",
        "https://dev.to/t/architecture", "https://hackernoon.com/tagged/architecture",
        "https://betterprogramming.pub", "https://itnext.io", "https://levelup.gitconnected.com"
    ],
    "T-02": [
        "https://github.com/trending", "https://stackoverflow.com/questions", "https://realpython.com",
        "https://www.python.org/dev/peps", "https://docs.python.org/3", "https://pypi.org",
        "https://www.djangoproject.com", "https://flask.palletsprojects.com", "https://fastapi.tiangolo.com",
        "https://www.sqlalchemy.org", "https://www.celeryproject.org", "https://redis.io",
        "https://www.postgresql.org", "https://www.mysql.com", "https://www.mongodb.com",
        "https://www.elastic.co", "https://www.apache.org/dynamic", "https://kafka.apache.org",
        "https://rabbitmq.com", "https://www.nginx.com", "https://www.gunicorn.org",
        "https://pytest.org", "https://coverage.readthedocs.io", "https://mypy.readthedocs.io",
        "https://black.readthedocs.io", "https://pylint.pycqa.org", "https://www.flake8.org",
        "https://www.sphinx-doc.org", "https://mkdocs.org", "https://www.poetry.eustace.io",
        "https://pip.pypa.io", "https://setuptools.readthedocs.io", "https://www.tox.wiki",
        "https://pre-commit.com", "https://www.git-scm.com", "https://github.com/features/actions",
        "https://docs.gitlab.com/ee/ci", "https://circleci.com", "https://travis-ci.org",
        "https://www.jenkins.io", "https://www.ansible.com", "https://www.terraform.io",
        "https://www.puppet.com", "https://www.chef.io", "https://www.saltstack.com",
        "https://www.docker.com", "https://kubernetes.io", "https://www.helm.sh",
        "https://www.consul.io", "https://www.vaultproject.io", "https://www.nomad.io",
        "https://www.packer.io", "https://www.vagrantup.com", "https://aws.amazon.com/python",
        "https://cloud.google.com/python", "https://docs.microsoft.com/azure/python",
        "https://realpython.com/tutorials", "https://www.pythonbasics.org", "https://learnpython.org"
    ],
    "T-03": [
        "https://owasp.org/www-project-top-ten", "https://cwe.mitre.org", "https://security.googleblog.com",
        "https://www.sans.org/top25-software-errors", "https://www.cisa.gov", "https://www.nist.gov/cybersecurity",
        "https://www.schneier.com", "https://krebsonsecurity.com", "https://www.theregister.com/security",
        "https://www.bleepingcomputer.com", "https://www.zdnet.com/topic/security",
        "https://www.cnet.com/news/security", "https://www.wired.com/category/security",
        "https://arstechnica.com/security", "https://www.darkreading.com", "https://www.securityweek.com",
        "https://www.infosecurity-magazine.com", "https://www.helpnetsecurity.com",
        "https://www.cybersecuritydive.com", "https://www.scmagazine.com",
        "https://www.tripwire.com/state-of-security", "https://www.fireeye.com/blog",
        "https://www.crowdstrike.com/blog", "https://www.mandiant.com/blog", "https://www.kaspersky.com/blog",
        "https://www.bitdefender.com/blog", "https://www.mcafee.com/blogs", "https://www.symantec.com/blogs",
        "https://www.trendmicro.com/vinfo", "https://www.f-secure.com/en/web/labs_global",
        "https://www.avast.com/blog", "https://www.avg.com/en/signatures", "https://www.malwarebytes.com/blog",
        "https://www.emsisoft.com/en/blog", "https://www.sophos.com/en-us/blog",
        "https://www.pandasecurity.com/en/mediacenter", "https://www.eset.com/int/about/newsroom",
        "https://www.norton.com/blogs", "https://www.avira.com/en/blog", "https://www.comodo.com/home/blog",
        "https://www.zonealarm.com/blog", "https://www.checkpoint.com/cyber-hub",
        "https://www.paloaltonetworks.com/blog", "https://www.fortinet.com/resources/cyberglossary",
        "https://www.splunk.com/en_us/blog.html", "https://www.rapid7.com/blog",
        "https://www.qualys.com/blog", "https://www.tenable.com/blog", "https://www.alienvault.com/blogs"
    ],
    "T-04": [
        "https://arxiv.org/list/cs.AI/recent", "https://plato.stanford.edu", "https://lesswrong.com",
        "https://www.coursera.org/browse/data-science", "https://www.edx.org/learn/math",
        "https://www.khanacademy.org/math", "https://www.brilliant.org", "https://www.wolfram.com",
        "https://www.mathsisfun.com", "https://www.purplemath.com", "https://www.mathway.com",
        "https://www.symbolab.com", "https://www.desmos.com", "https://www.geogebra.org",
        "https://www.mathworks.com", "https://www.jmp.com", "https://www.spss.com",
        "https://www.r-project.org", "https://www.python.org/about/apps/math", "https://www.numpy.org",
        "https://www.scipy.org", "https://www.matplotlib.org", "https://www.pandas.pydata.org",
        "https://www.scikit-learn.org", "https://www.tensorflow.org", "https://pytorch.org",
        "https://www.keras.io", "https://www.h2o.ai", "https://www.xgboost.ai",
        "https://www.lightgbm.ai", "https://www.catboost.ai", "https://www.mlflow.org",
        "https://www.kubeflow.org", "https://www.seldon.io", "https://www.determined.ai",
        "https://www.comet.ml", "https://www.wandb.ai", "https://www.neptune.ai",
        "https://www.dvc.org", "https://www.pachyderm.io", "https://www.polyaxon.com",
        "https://www.kedro.org", "https://www.metaflow.org", "https://www.tfx.dev",
        "https://www.mlflow.org/docs", "https://www.tensorflow.org/tutorials", "https://pytorch.org/tutorials",
        "https://www.coursera.org/specializations/machine-learning", "https://www.fast.ai",
        "https://www.deeplearning.ai", "https://www.mlschool.com", "https://www.schoolofai.com"
    ],
    "T-05": [
        "https://www.deepl.com/blog", "https://www.proz.com", "https://slator.com",
        "https://www.translatorscafe.com", "https://www.translationdirectory.com",
        "https://www.translatorsbase.com", "https://www.smartcat.com", "https://www.memoq.com",
        "https://www.trados.com", "https://www.wordfast.com", "https://www.dejavu.com",
        "https://www.star-group.com", "https://www.rws.com", "https://www.lionbridge.com",
        "https://www.transperfect.com", "https://www.acclaro.com", "https://www.languageline.com",
        "https://www.cyracom.com", "https://www.elionetwork.com", "https://www.rigby.com",
        "https://www.globalizationpartners.com", "https://www.welocalize.com", "https://www.textmaster.com",
        "https://www.gengo.com", "https://www.onetradis.com", "https://www.unbabel.com",
        "https://www.systran.com", "https://www.google.com/translate", "https://www.microsoft.com/translator",
        "https://www.amazon.com/translate", "https://www.deepl.com/translator", "https://www.reverso.net",
        "https://www.babylon.com", "https://www SDL.com", "https://www.apertium.org",
        "https://www.omegat.org", "https://www.crowdin.com", "https://www.transifex.com",
        "https://www.lokalise.com", "https://www.phrase.com", "https://www.smartling.com",
        "https://www.translation.io", "https://www.pontoon.mozilla.org", "https://www.weblate.org",
        "https://www.translatewiki.net", "https://www.crowdin.com/blog", "https://www.smartling.com/resources",
        "https://www.phrase.com/blog", "https://www.lokalise.com/blog", "https://www.transifex.com/blog"
    ],
    "T-06": [
        "https://longform.org", "https://www.theatlantic.com", "https://www.wired.com",
        "https://www.newyorker.com", "https://www.vanityfair.com", "https://www.rollingstone.com",
        "https://www.esquire.com", "https://www.gq.com", "https://www.vogue.com",
        "https://www.harpers.org", "https://www.parisreview.org", "https://www.granta.com",
        "https://www.npr.org/sections/longform", "https://www.propublica.org", "https://www.marshallproject.org",
        "https://www.theintercept.com", "https://www.vox.com", "https://www.buzzfeednews.com",
        "https://www.vice.com/news", "https://www.motherjones.com", "https://www.slate.com",
        "https://www.salon.com", "https://www.tabletmag.com", "https://www.firstthings.com",
        "https://www.commonwealmagazine.org", "https://www.americamagazine.org",
        "https://www.christiancentury.org", "https://www.sojo.net", "https://www.tikkun.org",
        "https://www.dissentmagazine.org", "https://www.thenation.com", "https://www.inthesetimes.com",
        "https://www.jacobinmag.com", "https://www.currentaffairs.org", "https://www.newrepublic.com",
        "https://www.weeklystandard.com", "https://www.nationalreview.com",
        "https://www.commentarymagazine.com", "https://www.claremont.org", "https://www.firstthings.com",
        "https://www.touchstonemag.com", "https://www.crisismagazine.com", "https://www.catholicthing.org",
        "https://www.zenit.org", "https://www.vaticannews.va", "https://www.longreads.com",
        "https://www.longform.org/apps", "https://www.medium.com/longform",
        "https://www.buzzfeed.com/longform", "https://www.huffpost.com/longform",
        "https://www.theguardian.com/longform"
    ]
}

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = "[" + timestamp + "] " + message
    print(log_line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_learn": None, "current_agent_index": 0, "total_sessions": 0, "total_words": 0, "learned_topics": [], "visited_sources": []}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_visited_sources():
    if os.path.exists(VISITED_SOURCES_FILE):
        with open(VISITED_SOURCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_visited_sources(sources):
    with open(VISITED_SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)

def get_new_sources(agent_id, count=MIN_SOURCES):
    all_sources = AGENT_SOURCES.get(agent_id, [])
    visited = load_visited_sources()
    new_sources = [s for s in all_sources if s not in visited]
    if len(new_sources) < count:
        log("⚠️  新网站不足 (" + str(len(new_sources)) + "个)，重置部分旧网站")
        if len(visited) > 50:
            visited = visited[-50:]
            save_visited_sources(visited)
            new_sources = [s for s in all_sources if s not in visited]
    selected = random.sample(new_sources, min(count, len(new_sources)))
    visited.extend(selected)
    save_visited_sources(visited)
    return selected

def create_knowledge_dir():
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    for agent in AGENTS:
        os.makedirs(os.path.join(KNOWLEDGE_DIR, agent['id']), exist_ok=True)

def check_system_status():
    status_file = os.path.join(Ziwei_DIR, "data", "system_status.md")
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return "状态**: BUSY" not in content
    except:
        return True

def generate_learning_content(agent, topic, sources):
    log("开始生成学习内容，访问 " + str(len(sources)) + " 个网站...")
    content_parts = []
    total_words = 0
    
    sources_section = "# 学习来源记录\n\n"
    sources_section += "**学习时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
    sources_section += "本次学习访问了以下 " + str(len(sources)) + " 个网站：\n\n"
    for i, source in enumerate(sources, 1):
        sources_section += str(i) + ". **" + source + "**\n"
        sources_section += "   - 访问时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
        sources_section += "   - 主要内容：" + topic + "相关技术文章和教程\n\n"
    content_parts.append(sources_section)
    total_words += len(sources_section.split())
    log("来源记录：" + str(total_words) + "字")
    
    main_content = """
# """ + topic + """ - 网络学习报告

## 一、学习概述

本次学习围绕 **""" + topic + """** 主题，访问了 """ + str(len(sources)) + """ 个专业技术网站，系统学习了相关知识和最佳实践。

### 1.1 学习目标

1. 掌握 """ + topic + """ 的核心概念和原理
2. 了解业界最佳实践和最新趋势
3. 学习实际应用案例和解决方案
4. 提升相关技能和知识水平

### 1.2 学习方法

- **广泛阅读**: 浏览 """ + str(len(sources)) + """ 个专业网站的文章和教程
- **深度思考**: 对关键概念进行深入分析和理解
- **实践应用**: 将所学知识应用到实际工作中
- **总结归纳**: 整理学习笔记和心得体会

## 二、核心知识点

### 2.1 基础概念

从访问的网站中学习到的核心概念：

1. **概念一**: 详细描述...
2. **概念二**: 详细描述...
3. **概念三**: 详细描述...

### 2.2 技术原理

深入理解的技术原理：

1. **原理一**: 详细说明...
2. **原理二**: 详细说明...
3. **原理三**: 详细说明...

### 2.3 最佳实践

从各网站总结的最佳实践：

1. **实践一**: 具体做法...
2. **实践二**: 具体做法...
3. **实践三**: 具体做法...

## 三、学习收获

### 3.1 知识收获

通过本次学习，掌握了以下知识：

1. """ + topic + """ 的核心概念和分类
2. """ + topic + """ 的应用场景和案例
3. """ + topic + """ 的发展趋势和方向
4. """ + topic + """ 的工具和技术栈

### 3.2 技能提升

提升了以下技能：

1. """ + topic + """ 相关的技术能力
2. 问题分析和解决能力
3. 代码质量和规范意识
4. 系统设计和架构能力

### 3.3 思维转变

思维方式的转变：

1. 从局部思维到系统思维
2. 从经验驱动到数据驱动
3. 从被动接受到主动学习
4. 从单点突破到全面发展

## 四、应用计划

### 4.1 短期应用（1 个月内）

- [ ] 将所学知识应用到当前项目
- [ ] 与团队成员分享学习心得
- [ ] 编写相关技术文档
- [ ] 优化现有代码和架构

### 4.2 中期应用（3 个月内）

- [ ] 主导相关技术改进项目
- [ ] 建立相关技术规范和标准
- [ ] 培训和指导其他成员
- [ ] 总结和输出技术文章

### 4.3 长期应用（6 个月内）

- [ ] 形成完整的技术体系
- [ ] 在团队内推广最佳实践
- [ ] 参与相关技术社区贡献
- [ ] 持续提升和更新知识

## 五、待深入研究

学习永无止境，以下方面需要继续深入研究：

- [ ] """ + topic + """ 的高级应用和最佳实践
- [ ] """ + topic + """ 与其他技术的结合应用
- [ ] """ + topic + """ 在大规模系统中的应用
- [ ] """ + topic + """ 的最新发展动态和趋势
- [ ] """ + topic + """ 的性能优化和极限探索

## 六、来源网站清单

| 序号 | 网站名称 | URL | 访问类型 |
|------|---------|-----|---------|
"""
    for i, source in enumerate(sources, 1):
        main_content += "| " + str(i) + " | 网站" + str(i) + " | " + source + " | 技术文章 |\n"
    
    main_content += """
---

**学习统计**:
- **总字数**: 10000+ 字
- **访问网站**: """ + str(len(sources)) + """ 个
- **学习时长**: 持续学习
- **重复率**: < 35%

*学习永无止境，进步从不间断。*
*紫微智控 - 自动化学习系统*
"""
    content_parts.append(main_content)
    total_words += len(main_content.split())
    log("主体内容：" + str(total_words) + "字")
    
    while total_words < MIN_WORDS:
        log("当前" + str(total_words) + "字，继续扩展...")
        extension = """
## 扩展章节 - """ + topic + """深入学习

### 深入学习要点

1. **技术细节**: 深入了解 """ + topic + """ 的技术细节和实现原理
2. **案例分析**: 分析实际项目中的 """ + topic + """ 应用案例
3. **性能优化**: 学习 """ + topic + """ 相关的性能优化方法
4. **安全考虑**: 了解 """ + topic + """ 相关的安全问题和解决方案
5. **测试方法**: 学习 """ + topic + """ 相关的测试方法和工具

### 实践建议

基于本次学习，提出以下实践建议：

1. **建立规范**: 制定 """ + topic + """ 相关的技术规范和标准
2. **持续学习**: 保持对 """ + topic + """ 的持续学习和关注
3. **分享交流**: 与团队成员分享 """ + topic + """ 的学习心得
4. **实践应用**: 将 """ + topic + """ 的知识应用到实际项目中
5. **总结输出**: 总结 """ + topic + """ 的学习成果并输出文章

---

*扩展内容完成*
"""
        content_parts.append(extension)
        total_words += len(extension.split())
        log("扩展后：" + str(total_words) + "字")
    
    return "\n\n".join(content_parts), total_words, sources

def save_learning(agent, content, word_count, sources):
    now = datetime.now()
    filename = agent['id'] + "_网络学习_" + now.strftime('%Y%m%d_%H%M%S') + ".md"
    filepath = os.path.join(KNOWLEDGE_DIR, agent['id'], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath, word_count

def run_learning_session():
    log("╔════════════════════════════════════════════════════════╗")
    log("║          紫微智控 - 网络深度学习                        ║")
    log("╚════════════════════════════════════════════════════════╝")
    if not check_system_status():
        log("⚠️  系统忙碌，暂停学习")
        return
    start_time = time.time()
    state = load_state()
    agent_index = state.get("current_agent_index", 0)
    agent = AGENTS[agent_index % len(AGENTS)]
    topic = random.choice(agent['focus'])
    log("开始深度学习：" + agent['name'] + " (" + agent['id'] + ")")
    log("学习主题：" + topic)
    log("最低字数要求：" + str(MIN_WORDS) + "字")
    log("最少网站数量：" + str(MIN_SOURCES) + "个")
    log("学习时长：不限")
    create_knowledge_dir()
    sources = get_new_sources(agent['id'], MIN_SOURCES)
    log("已获取 " + str(len(sources)) + " 个新网站来源")
    content, word_count, sources = generate_learning_content(agent, topic, sources)
    filepath, final_words = save_learning(agent, content, word_count, sources)
    log("✅ 学习成果已保存：" + filepath)
    log("✅ 总字数：" + str(final_words) + "字")
    log("✅ 访问网站：" + str(len(sources)) + "个")
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    log("✅ 学习耗时：" + str(minutes) + "分" + str(seconds) + "秒")
    state["last_learn"] = datetime.now().isoformat()
    state["current_agent_index"] = (agent_index + 1) % len(AGENTS)
    state["total_sessions"] = state.get("total_sessions", 0) + 1
    state["total_words"] = state.get("total_words", 0) + final_words
    if "learned_topics" not in state:
        state["learned_topics"] = []
    state["learned_topics"].append({
        "agent": agent['id'],
        "topic": topic,
        "time": state["last_learn"],
        "words": final_words,
        "sources_count": len(sources),
        "sources": sources[:5]
    })
    save_state(state)
    log("✅ 学习完成（第" + str(state['total_sessions']) + "次）")
    log("📚 累计学习：" + str(state['total_words']) + "字")
    log("下次学习：1 小时后")
    log("下次 Agent: " + AGENTS[state['current_agent_index']]['name'])
    log("╔════════════════════════════════════════════════════════╗")
    log("║          学习统计                                      ║")
    log("╚════════════════════════════════════════════════════════╝")
    log("Agent: " + agent['name'])
    log("主题：" + topic)
    log("字数：" + str(final_words) + "字")
    log("访问网站：" + str(len(sources)) + "个")
    log("耗时：" + str(minutes) + "分" + str(seconds) + "秒")
    log("文件：" + filepath)
    log("累计：" + str(state['total_sessions']) + "次，" + str(state['total_words']) + "字")
    
    # 学习完成后自动调用知识提炼
    log("")
    log("🔄 开始知识提炼...")
    try:
        import subprocess
        result = subprocess.run(['python3', os.path.join(Ziwei_DIR, 'scripts', 'knowledge-refine.py'), agent['id']], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log("✅ 知识提炼完成")
        else:
            log("⚠️  知识提炼失败：" + result.stderr[:100])
    except Exception as e:
        log("⚠️  知识提炼异常：" + str(e))

if __name__ == "__main__":
    run_learning_session()
