#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Запуск инфраструктуры..."

docker-compose up -d

echo "⏳ Ожидание готовности сервисов..."

max_attempts=30
attempt=0

wait_for_service() {
    local service=$1
    local check_cmd=$2
    
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if eval "$check_cmd" > /dev/null 2>&1; then
            echo "✅ $service готов"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo "❌ $service не готов после $max_attempts попыток"
    return 1
}

wait_for_service "PostgreSQL" "docker exec api_tests_postgres pg_isready -U tester -d api_tests"
wait_for_service "Zookeeper" "nc -z localhost 2181"
wait_for_service "Kafka" "docker exec api_tests_kafka kafka-broker-api-versions --bootstrap-server localhost:9092"

echo "✅ Все сервисы готовы"
echo ""
echo "🧪 Запуск тестов многопоточно..."

pytest -n auto --alluredir=reports/allure-results "$@"

echo ""
echo "✅ Тесты завершены"
echo "📊 Для просмотра Allure отчёта: allure serve reports/allure-results"

