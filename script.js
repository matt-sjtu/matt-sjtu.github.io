function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    const isHidden = dropdown.style.display === '' || dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'block' : 'none';
}

const translations = {
    'zh-CN': {
        langToggle: 'EN',
        docLang: 'zh-CN',
        eyebrow: '上海交通大学 | 清源研究院',
        welcome: '张健夫',
        roleSubtitle: '助理教授 · 人工智能 & 计算机视觉',
        nav: { about: '关于', research: '研究', courses: '教学', contact: '联系' },
        aboutCaption: '学术简介',
        aboutTitle: '科研与教学',
        aboutContent: '上海交通大学电子信息与电气工程学院清源研究院助理教授。本科毕业于上海交通大学 ACM 班，博士毕业于上海交通大学计算机科学与工程系，师从 <a href="https://bcmi.sjtu.edu.cn/~zhangliqing/" target="_blank">张丽清教授</a>、<a href="https://apex.sjtu.edu.cn/members/yyu" target="_blank">俞勇教授</a> 与 <a href="https://qibinzhao.github.io/" target="_blank">赵启斌博士</a>，长期从事人工智能与计算机视觉研究。',
        metaPosition: '助理教授，上海交通大学清源研究院 / 电子信息与电气工程学院',
        metaEducation: '上海交通大学计算机科学与工程系博士；ACM 班学士',
        metaAdvisor: '合作/指导：张丽清教授、俞勇教授、赵启斌博士',
        researchCaption: 'Research',
        researchTitle: '可信视觉与生成模型',
        researchContent: '研究聚焦可信的视觉基础模型与生成式模型，涵盖自监督预训练、可解释性与可靠性、多模态感知以及人机协同 AI。代表性成果与最新工作可在 <a href="https://scholar.google.com/citations?hl=en&user=jSiStc4AAAAJ" id="google-scholar-link" target="_blank">Google Scholar</a> 与 <a href="job2024.pdf" id="recent-work-link" target="_blank">近期工作</a> 中查看。',
        focus: ['基础模型', '生成式视觉', '可信 AI', '自监督 / 多模态'],
        scholarCardCaption: '学术成果',
        scholarCardTitle: 'Google Scholar',
        scholarCardDesc: '持续产出在人工智能与计算机视觉领域的研究成果，涵盖生成模型、可解释性和可靠性等方向。',
        scholarButton: '查看引用与论文',
        recentWorkButton: '近期工作概览',
        collabCardCaption: '合作与团队',
        collabCardTitle: '开放合作',
        collabCardDesc: '欢迎对生成式视觉、可解释性与可信 AI 感兴趣的学生与研究者联系，共同推进交叉创新。',
        coursesCaption: 'Teaching',
        coursesTitle: '课程与讲义',
        course1: 'CS3964 图像处理与视觉',
        course1Badge: '本科课程',
        course1Intro: '导论',
        course1Geometry: '几何模型',
        course1Statistics: '统计模型',
        course1Deep: '深度模型',
        course1Generation: '图像生成',
        course2: 'CS7353 设计和理解深度神经网络',
        course2Badge: '研究生课程',
        course3: 'CS3969 视觉内容生成',
        course3Badge: '本科课程',
        contactCaption: 'Contact',
        contactTitle: '联系与合作',
        contactContent: '邮箱：c [dot] sis [at] sjtu [dot] edu [dot] cn。期待与对生成式视觉、可信 AI 及相关交叉方向感兴趣的同仁交流合作。',
        footer: '© 2024 张健夫 | Qingyuan Institute, Shanghai Jiao Tong University'
    },
    en: {
        langToggle: 'CN',
        docLang: 'en',
        eyebrow: 'Shanghai Jiao Tong University | Qingyuan Institute',
        welcome: 'Jianfu Zhang',
        roleSubtitle: 'Assistant Professor · AI & Computer Vision',
        nav: { about: 'About', research: 'Research', courses: 'Teaching', contact: 'Contact' },
        aboutCaption: 'Profile',
        aboutTitle: 'Scholarship & Teaching',
        aboutContent: 'Assistant Professor at the Qingyuan Institute and the School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong University. I received my B.S. from the SJTU ACM Honors Class and Ph.D. from the Department of Computer Science and Engineering, advised by <a href="https://bcmi.sjtu.edu.cn/~zhangliqing/" target="_blank">Prof. Liqing Zhang</a>, <a href="https://apex.sjtu.edu.cn/members/yyu" target="_blank">Prof. Yong Yu</a>, and <a href="https://qibinzhao.github.io/" target="_blank">Dr. Qibin Zhao</a>.',
        metaPosition: 'Assistant Professor, Qingyuan Institute / School of EIEE, SJTU',
        metaEducation: 'Ph.D. & B.S., Computer Science and Engineering, SJTU',
        metaAdvisor: 'Mentors: Prof. Liqing Zhang, Prof. Yong Yu, Dr. Qibin Zhao',
        researchCaption: 'Research',
        researchTitle: 'Trustworthy Vision & Generative Models',
        researchContent: 'Working on trustworthy vision foundation and generative models spanning self-supervised pretraining, interpretability and reliability, multimodal perception, and human-AI collaboration. Representative works are available on <a href="https://scholar.google.com/citations?hl=en&user=jSiStc4AAAAJ" id="google-scholar-link" target="_blank">Google Scholar</a> and in my <a href="job2024.pdf" id="recent-work-link" target="_blank">recent work</a>.',
        focus: ['Foundation Models', 'Generative Vision', 'Trustworthy AI', 'Self-supervision / Multimodal'],
        scholarCardCaption: 'Scholarship',
        scholarCardTitle: 'Google Scholar',
        scholarCardDesc: 'Continuous publications in AI and computer vision, covering generative modeling, interpretability, and reliability.',
        scholarButton: 'View citations & papers',
        recentWorkButton: 'Recent highlights',
        collabCardCaption: 'Collaboration',
        collabCardTitle: 'Open to Collaborate',
        collabCardDesc: 'Looking for students and collaborators interested in generative vision, interpretability, and trustworthy AI.',
        coursesCaption: 'Teaching',
        coursesTitle: 'Courses & Materials',
        course1: 'CS3964 Image Processing and Vision',
        course1Badge: 'Undergraduate',
        course1Intro: 'Introduction',
        course1Geometry: 'Geometric Models',
        course1Statistics: 'Statistical Models',
        course1Deep: 'Deep Models',
        course1Generation: 'Image Generation',
        course2: 'CS7353 Designing and Understanding Deep Neural Networks',
        course2Badge: 'Graduate',
        course3: 'CS3969 Visual Content Generation',
        course3Badge: 'Undergraduate',
        contactCaption: 'Contact',
        contactTitle: 'Contact & Collaboration',
        contactContent: 'Email: c [dot] sis [at] sjtu [dot] edu [dot] cn. Happy to discuss collaborations on generative vision, trustworthy AI, and related intersections.',
        footer: '© 2024 Jianfu Zhang | Qingyuan Institute, Shanghai Jiao Tong University'
    }
};

function applyTranslations(lang) {
    const t = translations[lang];
    document.documentElement.lang = t.docLang;

    const setters = [
        ['eyebrow', t.eyebrow],
        ['welcome', t.welcome],
        ['role-subtitle', t.roleSubtitle],
        ['nav-about', t.nav.about],
        ['nav-research', t.nav.research],
        ['nav-courses', t.nav.courses],
        ['nav-contact', t.nav.contact],
        ['about-caption', t.aboutCaption],
        ['about-title', t.aboutTitle],
        ['meta-position', t.metaPosition],
        ['meta-education', t.metaEducation],
        ['meta-advisor', t.metaAdvisor],
        ['research-caption', t.researchCaption],
        ['research-title', t.researchTitle],
        ['scholar-card-caption', t.scholarCardCaption],
        ['scholar-card-title', t.scholarCardTitle],
        ['scholar-card-desc', t.scholarCardDesc],
        ['scholar-button', t.scholarButton],
        ['recent-work-button', t.recentWorkButton],
        ['collab-card-caption', t.collabCardCaption],
        ['collab-card-title', t.collabCardTitle],
        ['collab-card-desc', t.collabCardDesc],
        ['courses-caption', t.coursesCaption],
        ['courses-title', t.coursesTitle],
        ['course1-link', t.course1],
        ['course1-badge', t.course1Badge],
        ['course1-intro-link', t.course1Intro],
        ['course1-geometry-link', t.course1Geometry],
        ['course1-statistics-link', t.course1Statistics],
        ['course1-deep-link', t.course1Deep],
        ['course1-generation-link', t.course1Generation],
        ['course2-link', t.course2],
        ['course2-badge', t.course2Badge],
        ['course3-link', t.course3],
        ['course3-badge', t.course3Badge],
        ['contact-caption', t.contactCaption],
        ['contact-title', t.contactTitle],
        ['footer-text', t.footer]
    ];

    setters.forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    });

    const htmlSetters = [
        ['about-content', t.aboutContent],
        ['research-content', t.researchContent],
        ['contact-content', t.contactContent]
    ];

    htmlSetters.forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = value;
    });

    document.querySelectorAll('[data-focus-index]').forEach((el) => {
        const idx = Number(el.dataset.focusIndex);
        el.textContent = t.focus[idx] || '';
    });

    const toggleButton = document.getElementById('language-toggle');
    toggleButton.textContent = t.langToggle;
}

document.getElementById('language-toggle').addEventListener('click', () => {
    const nextLang = document.documentElement.lang === 'zh-CN' ? 'en' : 'zh-CN';
    applyTranslations(nextLang);
});

// Initialize with default language content
applyTranslations(document.documentElement.lang || 'zh-CN');
