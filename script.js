<script>
    // Пример: Ереван основан в 782 году до н.э.
    const yerevanFounded = -782; // отрицательное число для до н.э.
    const currentYear = new Date().getFullYear();
    
    // вычисляем возраст
    const age = currentYear - yerevanFounded;
    
    document.getElementById('yerevan-age').textContent = age;
</script>