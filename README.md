## Description

A robust Python parser designed to extract product listings from specific sellers on Drom.ru (a leading Russian automotive marketplace). This tool navigates the site's anti-scraping protections, collects detailed item data, and generates an XML feed for further use. Developed in 2021, it has been running reliably in production with minimal changes ever since.

## Key Functionalities

*   **Product Data Scraping:** Parses product details from a provided list of Drom item URLs.
*   **XML Feed Generation:** Compiles the collected data into a structured XML feed.
*   **Telegram Monitoring:** Sends comprehensive status reports (start, progress, completion, errors) to a dedicated Telegram channel for team visibility.
*   **Advanced Anti-Blocking Strategy:** Implements a unique scraping strategy to bypass sophisticated anti-bot measures.

## Tech Stack

*   Python
*   Requests / HTTPX
*   BeautifulSoup / lxml
*   AWS EC2 (Free Tier)
*   Telegram Bot API

## Project Context & Development Notes

This project was a significant challenge, with about three weeks of development time dedicated primarily to researching a viable scraping strategy against Drom's robust defenses.

**The Core Challenge:** After ~20-25 requests, Drom presented a complex captcha that could only be solved manually at the time, halting automation.

**Evaluated & Rejected Solutions:**
1.  **Manual Captcha Solving:** Infeasible for parsing ~2000 pages.
2.  **Captcha Solving Services:** Resulted in unacceptable slowdowns and unreliable success rates.
3.  **Frequent Proxy Rotation:** Deemed too costly for the required scale.

**The Implemented Solution:** A cost-effective and scalable approach using **AWS Free Tier**. By leveraging Amazon's vast pool of IP addresses from different EC2 instances, the script mimics organic traffic from various sources, effectively bypassing request limits without triggering captchas. This strategy, combined with an annual AWS account rotation, has proven successful for years.

**Evolution:** The initial link collection module became obsolete due to site updates. It was replaced by a separate, simple Windows desktop tool that the client runs to gather URLs, which are then uploaded to the server for processing by this main script.

## Why It's Here

This repository demonstrates my ability to:

*   Tackle complex scraping tasks against well-protected websites.
*   Conduct deep R&D to find innovative, cost-effective technical solutions.
*   Develop stable, long-lasting automation that requires minimal maintenance.
*   Architect flexible systems that can adapt when one component (link collection) becomes obsolete.
*   Build transparent processes with integrated monitoring for non-technical stakeholders.

---

## Описание

Надёжный парсер на Python, разработанный для сбора списков товаров со страниц определённых продавцов на Drom. Этот инструмент обходит защиту сайта от парсинга, собирает детальную информацию о товарах и формирует XML-фид для дальнейшего использования. Написанный в 2021 году, он стабильно работает в продакшене с тех пор практически без изменений.

## Ключевые функции

*   **Сбор данных о товарах:** Парсит детали товаров из предоставленного списка ссылок Drom.
*   **Генерация XML-фида:** Компилирует собранные данные в структурированный XML-фид, с сохранением данных в промежуточных pickle-файлах, для обеспечения постоянства id товаров.
*   **Мониторинг в Telegram:** Отправляет подробные отчеты о статусе (старт, прогресс, завершение, ошибки) в выделенный Telegram-канал для информирования команды.
*   **Стратегия обхода блокировок:** Реализует стратегию парсинга для обхода сложной анти-бот защиты.

## Стек технологий

*   Python
*   Requests / HTTPX
*   BeautifulSoup / lxml
*   AWS EC2 (Free Tier)
*   Telegram Bot API

## Контекст проекта и заметки о разработке

Этот проект представлял собой значительный вызов, где около трех недель разработки ушло только на поиск работоспособной стратегии парсинга в условиях сильной защиты Drom.

**Основная проблема:** После ~20-25 запросов Drom показывал сложную капчу, которую в то время можно было решить только вручную, что останавливало автоматизацию.

**Оцененные и отклоненные решения:**
1.  **Ручной ввод капчи:** Нецелесообразно для обработки ~2000 страниц.
2.  **Сервисы по решению капчи:** Приводили к неприемлемому замедлению и ненадёжному результату.
3.  **Частая смена прокси:** Была признана слишком дорогой для требуемого масштаба.

**Реализованное решение:** Экономически эффективный и масштабируемый подход с использованием **AWS Free Tier**. Используя огромный пул IP-адресов от разных EC2-инстансов Amazon, скрипт имитирует органический трафик из различных источников, эффективно обходя лимиты запросов без активации капчи. Эта стратегия в сочетании с ежегодной сменой AWS-аккаунта успешно работает до сих пор.

**Эволюция:** Изначальный модуль сбора ссылок устарел из-за обновлений сайта. Он был заменен на отдельную простую десктопную программу для Windows, которую клиент запускает для сбора URL. Эти ссылки автоматически загружаются на сервер для обработки этим основным скриптом.

## Почему этот проект здесь

Этот репозиторий демонстрирует мои способности:

*   Решать сложные задачи парсинга хорошо защищенных веб-сайтов.
*   Проводить глубокие R&D для поиска инновационных и рентабельных технических решений.
*   Создавать стабильные, долговременные системы автоматизации, требующие минимального обслуживания.
*   Архитектурно проектировать гибкие системы, которые могут адаптироваться при устаревании отдельных компонентов (как сборщик ссылок).
*   Создавать прозрачные процессы со встроенным мониторингом для нетехнических участников команды.