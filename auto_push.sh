#!/bin/bash

while true
do
    git add .
    git commit -m "Автоматическое обновление: $(date)"
    git push origin main
    sleep 300  # Пауза 5 минут между обновлениями
done 