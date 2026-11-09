#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 ../ 下的课程 Markdown 打包进 template.html，生成单文件静态站点 index.html。
修改课程内容后重新运行:  python3 build.py
"""
import json
import hashlib
import pathlib
import re
from urllib.parse import unquote

HERE = pathlib.Path(__file__).resolve().parent
COURSE_DIR = HERE.parent
CN_NUM = '一二三四五'
# 课程导航次序；分阶段按章节选择的具体顺序以 README 为准。
ORDER = [f'{n:02d}' for n in range(1, 27)]
STAGE_BY_ID = {k: i for i, ids in enumerate(('01 02 03 04 05 06', '07 08 09 10 11 12', '13 14 15 16 17', '18 19 20 21 22', '23 24 25 26'), 1) for k in ids.split()}


def parse_lesson(path: pathlib.Path) -> dict:
    md = path.read_text(encoding='utf-8')
    lesson_id = path.name[:2]
    lines = md.split('\n')

    title = ''
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        lines = lines[1:]

    # 去掉文件头部的元信息引用块（> **所属阶段**：… 等与装饰性分隔线）
    meta = {}
    while lines:
        s = lines[0].strip()
        if s.startswith('>'):
            m = re.match(r'>\s*\*\*(.+?)\*\*[：:]\s*(.*)', s)
            if m:
                meta[m.group(1).strip()] = m.group(2).strip()
            lines = lines[1:]
        elif s in ('', '---'):
            lines = lines[1:]
        else:
            break

    body = '\n'.join(lines).strip()
    # 站内 .md 链接转为课程路由；sim: 链接转为仿真弹窗路由
    body = re.sub(r'\]\((\d{2})-[^)]*\.md\)', r'](#/lesson/\1)', body)
    body = re.sub(r'\]\(sim:([A-Za-z0-9_-]+)\)', r'](#/sim/\1)', body)

    stage_txt = meta.get('所属阶段', '')
    stage = 1
    m = re.search(r'阶段([一二三四五])', stage_txt)
    if m:
        stage = CN_NUM.index(m.group(1)) + 1
    else:
        stage = 1 if lesson_id < '04' else 2 if lesson_id < '08' else 3 if lesson_id < '11' else 4 if lesson_id < '15' else 5

    stage = STAGE_BY_ID[lesson_id]
    diff = meta.get('本课难度', '').count('⭐')
    prev = meta.get('前置课程', '')

    short = re.sub(r'^第\s*\d+\s*课\s*·\s*', '', title)
    short = re.sub(r'^项目实战\s*·\s*', '', short)
    if lesson_id in ('22', '23', '25'):
        short = re.sub(r'\s*（选学）$', '', short)
    return {
        'id': lesson_id,
        'title': title,
        'short': short,
        'stage': stage,
        'diff': max(1, min(5, diff)),
        'prev': prev,
        'optional': lesson_id in ('22', '23', '25'),
        'md': body,
        # 备份恢复时检查每课任务的内容和次序，避免错位。
        'taskSignature': hashlib.sha256('\n'.join(
            line.strip() for line in body.splitlines()
            if re.match(r'^\s*-\s+\[[ xX]\]\s+', line)
        ).encode('utf-8')).hexdigest(),
        'taskCount': sum(bool(re.match(r'^\s*-\s+\[[ xX]\]\s+', line)) for line in body.splitlines()),
    }


def collect_resources():
    """把新增专题资料连同站内相对 Markdown 链接打包进单文件。"""
    paths = []
    exercise_dir = COURSE_DIR / '基础练习'
    car_dir = COURSE_DIR / '项目资料' / '纯硬件循迹小车'
    led_dir = COURSE_DIR / '项目资料' / '首块LED练习板'
    stm32_dir = COURSE_DIR / '项目资料' / '11-STM32'
    sim_review_dir = COURSE_DIR / '仿真审核'
    for folder in (exercise_dir, car_dir, led_dir, stm32_dir, sim_review_dir):
        if folder.exists():
            paths.extend(sorted(folder.rglob('*.md')))
    exercise_file = COURSE_DIR / '基础练习与实验记录手册.md'
    if exercise_file.is_file():
        paths.append(exercise_file)
    analog_file = COURSE_DIR / '模拟电路进阶练习.md'
    if analog_file.is_file():
        paths.append(analog_file)
    mapping_file = COURSE_DIR / '课件内容与课程对照核验表-2026-11-02.md'
    if mapping_file.is_file():
        paths.append(mapping_file)
    plan_file = COURSE_DIR / '基于零基础课件的课程完善与重规划方案-2026-11-02.md'
    if plan_file.is_file():
        paths.append(plan_file)
    implementation_file = COURSE_DIR / '2026-11-02-课程完善实施记录.md'
    if implementation_file.is_file():
        paths.append(implementation_file)
    paths = [p for p in paths if p.is_file()]
    id_by_path = {p.resolve(): hashlib.sha256(str(p.relative_to(COURSE_DIR)).encode('utf-8')).hexdigest()[:16] for p in paths}
    result = []
    for path in paths:
        md = path.read_text(encoding='utf-8')
        def link(match):
            target = unquote(match.group(2))
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                return match.group(0)
            if re.fullmatch(r'sim:[A-Za-z0-9_-]+', target):
                return '[' + match.group(1) + '](#/sim/' + target[4:] + ')'
            file_part, sep, fragment = target.partition('#')
            resolved = (path.parent / file_part).resolve()
            if resolved in id_by_path:
                # 站内专题独立页面暂不支持跨页标题锚点，仍保留到目标文档入口。
                return '[' + match.group(1) + '](#/resource/' + id_by_path[resolved] + ')'
            lesson = re.match(r'^(\d{2})-.*\.md$', resolved.name)
            if resolved.parent == COURSE_DIR and lesson and lesson.group(1) in ORDER:
                return '[' + match.group(1) + '](#/lesson/' + lesson.group(1) + ')'
            # 未打包的本地路径无法在单文件站点访问，避免生成失效链接。
            return match.group(1) + '（本地项目资料，站点未打包）'
        md = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, md)
        first = next((line[2:].strip() for line in md.splitlines() if line.startswith('# ')), path.stem)
        group = ('审核与实施记录' if sim_review_dir in path.parents or path == implementation_file else
                 '基础练习' if exercise_dir in path.parents or path in (exercise_file, analog_file, mapping_file, plan_file) else
                 'STM32 工程资料' if stm32_dir in path.parents else
                 '首块 LED 练习板' if led_dir in path.parents else '纯硬件循迹小车')
        result.append({'id': id_by_path[path.resolve()], 'title': first, 'md': md,
                       'path': str(path.relative_to(COURSE_DIR)), 'group': group})
    return result


def main():
    files = sorted(COURSE_DIR.glob('[0-9][0-9]-*.md'))
    if not files:
        raise SystemExit(f'未找到课程文件: {COURSE_DIR}')
    lessons = [parse_lesson(p) for p in files]
    lessons.sort(key=lambda lesson: ORDER.index(lesson['id']))

    resources = collect_resources()
    resource_paths = {r['path']: r['id'] for r in resources}
    for lesson in lessons:
        for path, resource_id in resource_paths.items():
            lesson['md'] = lesson['md'].replace('](' + path + ')', '](#/resource/' + resource_id + ')')
    readme = (COURSE_DIR / 'README.md').read_text(encoding='utf-8')
    # 若课程编号对照表仍在，则嵌入首页；精简版没有该文件时跳过。
    mapping_path = COURSE_DIR / '课程编号对照与整合记录-2026-10-29.md'
    if mapping_path.is_file():
        mapping = mapping_path.read_text(encoding='utf-8')
        table = '\n'.join(line for line in mapping.splitlines() if line.startswith('|'))
        readme = readme.replace('[课程编号对照与整合记录](课程编号对照与整合记录-2026-10-29.md)', '下方的课程编号对照表')
        readme += '\n\n## 课程编号对照表\n\n' + table + '\n'
    readme = re.sub(r'\]\((\d{2})-[^)]*\.md\)', r'](#/lesson/\1)', readme)
    readme = re.sub(r'\]\(sim:([A-Za-z0-9_-]+)\)', r'](#/sim/\1)', readme)
    for path, resource_id in resource_paths.items():
        readme = readme.replace('](' + path + ')', '](#/resource/' + resource_id + ')')
    readme_lines = readme.split('\n')
    if readme_lines and readme_lines[0].startswith('# '):
        readme_lines = readme_lines[1:]
    readme = '\n'.join(readme_lines).strip()

    data = {
        'title': 'PCB 设计系统教学课程',
        'lessons': lessons,
        'readmeMd': readme,
        'resources': resources,
    }

    # 本地笔记可保留资料的真实位置；生成可发布网页时隐藏本机绝对路径。
    def hide_local_paths(value):
        if isinstance(value, str):
            return re.sub(r'(?<![\w:/])/(?:Users|home|Volumes)/[^\s`<>"\)\]]+', '[本机资料路径已隐藏]', value)
        if isinstance(value, list):
            return [hide_local_paths(item) for item in value]
        if isinstance(value, dict):
            return {key: hide_local_paths(item) for key, item in value.items()}
        return value

    payload = json.dumps(hide_local_paths(data), ensure_ascii=False, separators=(',', ':'))
    payload = payload.replace('</', '<\\/')  # 防止内容中出现 </script> 截断

    template = (HERE / 'template.html').read_text(encoding='utf-8')
    assert template.count('__COURSE_DATA_JSON__') == 1, '模板占位符异常'
    html = template.replace('__COURSE_DATA_JSON__', payload)
    out = HERE / 'index.html'
    out.write_text(html, encoding='utf-8')

    print(f'✅ 已生成 {out.name}（{out.stat().st_size/1024:.0f} KB）')
    print(f'   课程 {len(lessons)} 篇')
    for l in lessons:
        print(f'   {l["id"]} {l["short"]:<24} 阶段{l["stage"]} 难度{"*"*l["diff"]}')


if __name__ == '__main__':
    main()
