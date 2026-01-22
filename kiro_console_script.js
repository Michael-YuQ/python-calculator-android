// ============================================================
// Kiro DOM 检查脚本
// 在 Kiro 中按 Ctrl+Shift+I，然后在 Console 中粘贴运行
// ============================================================

console.log('🔍 开始检查 Kiro DOM 结构...\n');

// 1. 查找所有输入元素
console.log('=' .repeat(60));
console.log('所有输入元素:');
console.log('=' .repeat(60));

const inputs = document.querySelectorAll('input, textarea, [contenteditable="true"]');

inputs.forEach((input, index) => {
    const rect = input.getBoundingClientRect();
    
    // 只显示可见的元素
    if (rect.width > 0 && rect.height > 0) {
        console.log(`\n[${index}] ${input.tagName} (${input.type || 'N/A'})`);
        
        if (input.id) console.log(`    ID: ${input.id}`);
        if (input.className) console.log(`    Class: ${input.className}`);
        if (input.placeholder) console.log(`    Placeholder: ${input.placeholder}`);
        if (input.name) console.log(`    Name: ${input.name}`);
        
        console.log(`    位置: (${Math.round(rect.x)}, ${Math.round(rect.y)})`);
        console.log(`    大小: ${Math.round(rect.width)} x ${Math.round(rect.height)}`);
        
        // 生成选择器
        let selector = input.tagName.toLowerCase();
        if (input.id) {
            selector = `#${input.id}`;
        } else if (input.className) {
            const classes = input.className.split(' ').filter(c => c).slice(0, 2).join('.');
            if (classes) selector += `.${classes}`;
        }
        
        console.log(`    选择器: ${selector}`);
        
        // 保存到全局变量以便后续使用
        window[`input${index}`] = input;
        console.log(`    💡 可以使用 input${index} 访问此元素`);
    }
});

console.log('\n' + '=' .repeat(60));
console.log('💡 使用提示:');
console.log('=' .repeat(60));
console.log('\n1. 查看某个元素: input0, input1, ...');
console.log('2. 获取元素位置: input0.getBoundingClientRect()');
console.log('3. 输入文本: input0.value = "继续"');
console.log('4. 触发输入事件: input0.dispatchEvent(new Event("input", {bubbles: true}))');
console.log('5. 按回车: input0.dispatchEvent(new KeyboardEvent("keydown", {key: "Enter", keyCode: 13, bubbles: true}))');

console.log('\n' + '=' .repeat(60));
console.log('查找特定位置的元素:');
console.log('=' .repeat(60));

// 2. 提供一个函数来查找特定位置的元素
window.findElementAt = function(x, y) {
    const element = document.elementFromPoint(x, y);
    
    if (!element) {
        console.log(`❌ 位置 (${x}, ${y}) 没有找到元素`);
        return null;
    }
    
    const rect = element.getBoundingClientRect();
    
    console.log(`\n✅ 找到元素:`);
    console.log(`   标签: ${element.tagName}`);
    if (element.id) console.log(`   ID: ${element.id}`);
    if (element.className) console.log(`   Class: ${element.className}`);
    if (element.type) console.log(`   Type: ${element.type}`);
    if (element.placeholder) console.log(`   Placeholder: ${element.placeholder}`);
    console.log(`   位置: (${Math.round(rect.x)}, ${Math.round(rect.y)})`);
    console.log(`   大小: ${Math.round(rect.width)} x ${Math.round(rect.height)}`);
    
    // 生成选择器
    let selector = element.tagName.toLowerCase();
    if (element.id) {
        selector = `#${element.id}`;
    } else if (element.className) {
        const classes = element.className.split(' ').filter(c => c).slice(0, 2).join('.');
        if (classes) selector += `.${classes}`;
    }
    console.log(`   选择器: ${selector}`);
    
    window.foundElement = element;
    console.log(`\n💡 元素已保存到 foundElement 变量`);
    
    return element;
};

console.log('\n💡 使用 findElementAt(x, y) 查找特定位置的元素');
console.log('   例如: findElementAt(1228, 720)');

console.log('\n' + '=' .repeat(60));
console.log('自动输入函数:');
console.log('=' .repeat(60));

// 3. 提供一个自动输入函数
window.autoInput = function(selector, text, pressEnter = true) {
    const element = document.querySelector(selector);
    
    if (!element) {
        console.log(`❌ 未找到元素: ${selector}`);
        return false;
    }
    
    console.log(`✅ 找到元素: ${selector}`);
    
    // 聚焦
    element.focus();
    console.log('   已聚焦');
    
    // 输入文本
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (element.contentEditable === 'true') {
        element.textContent = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    console.log(`   已输入: ${text}`);
    
    // 按回车
    if (pressEnter) {
        const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true
        });
        element.dispatchEvent(event);
        console.log('   已按回车');
    }
    
    return true;
};

console.log('\n💡 使用 autoInput(selector, text) 自动输入');
console.log('   例如: autoInput("textarea", "继续")');
console.log('   例如: autoInput("#chat-input", "继续", false)  // 不按回车');

console.log('\n' + '=