# 🎯 GUIA COMPLETO: Criar Flow NiFi Manualmente

## 🚨 **Situação Atual**
- ❌ Templates XML não funcionam (erro de formato)
- ✅ NiFi rodando em: https://localhost:8443/nifi/  
- ✅ Dados CSV disponíveis em: `/opt/nifi/input/amazon/`
- 🔐 Login: `nifi` / `HGd15bvfv8744ghbdhgdv7895agqERAo`

## 📋 **PASSO A PASSO DETALHADO**

### **1. 🔐 Acesso e Login**
```
URL: https://localhost:8443/nifi/
Usuário: nifi
Senha: HGd15bvfv8744ghbdhgdv7895agqERAo
```

### **2. 🎯 Criar Flow Básico (GetFile → LogMessage)**

#### **Passo 2.1: Adicionar GetFile**
1. **Canvas principal** → **Botão direito do mouse**
2. **"Add Processor"** ou ícone de engrenagem
3. **Campo de busca**: digite `GetFile`
4. **Selecionar**: `GetFile` da lista
5. **Click "Add"** ou arrastar para o canvas

#### **Passo 2.2: Configurar GetFile**
1. **Duplo-click** no processador GetFile
2. **Aba "Properties"**
3. **Configurar**:
   ```
   Input Directory: /opt/nifi/input/amazon
   File Filter: .*\.csv
   Keep Source File: true
   Polling Interval: 10 sec
   Minimum File Age: 1 sec
   ```
4. **Click "Apply"**

#### **Passo 2.3: Adicionar LogMessage**
1. **Canvas** → **Botão direito** → **"Add Processor"**
2. **Buscar**: `LogMessage`
3. **Selecionar**: `LogMessage`
4. **Add** ou arrastar para o canvas

#### **Passo 2.4: Configurar LogMessage**
1. **Duplo-click** no LogMessage
2. **Aba "Properties"**:
   ```
   Log Level: info
   Log prefix: AMAZON_CSV_PROCESSED: 
   Log Payload: false
   Attributes to Log CSV: filename,absolute.path,file.size
   ```
3. **Apply**

#### **Passo 2.5: Conectar Processadores**
1. **Hover** sobre o processador GetFile
2. **Aparece uma seta** → **Arrastar até LogMessage**
3. **Pop-up "Create Connection"**:
   - **Marcar**: `success`
   - **Click "Add"**

#### **Passo 2.6: Configurar Auto-terminate**
1. **Duplo-click** em LogMessage
2. **Aba "Relationships"**
3. **Marcar**: `success` como **auto-terminated**
4. **Apply**

### **3. 🚀 Testar o Flow**

#### **Passo 3.1: Iniciar Processadores**
1. **Selecionar GetFile** (click)
2. **Botão "Start"** (▶️) na toolbar
3. **Repetir para LogMessage**

#### **Passo 3.2: Verificar Funcionamento**
1. **Aguardar 10-15 segundos**
2. **Verificar "Bulletin Board"** (ícone de aviso no canto superior direito)
3. **Logs devem mostrar**: "AMAZON_CSV_PROCESSED: books_data.csv"

### **4. 📊 Expandir para Flow Completo**

#### **Depois que o básico funcionar, adicionar:**

1. **SplitText** (entre GetFile e LogMessage):
   ```
   Line Split Count: 1000
   Header Line Count: 1
   ```

2. **ConvertRecord**:
   ```
   Record Reader: CSVReader (criar Controller Service)
   Record Writer: JsonRecordSetWriter (criar Controller Service)
   ```

3. **PutDatabaseRecord**:
   ```
   Database Connection: PostgreSQL Pool (criar Controller Service)
   Table Name: bronze.amazon_books
   ```

## 🛠️ **Controller Services Necessários**

### **CSV Reader Service**
```
Type: CSVReader
Name: CSV-Reader-Amazon
Properties:
  - CSV Format: RFC4180
  - Value Separator: ,
  - First Line is Header: true
```

### **JSON Writer Service**
```  
Type: JsonRecordSetWriter
Name: JSON-Writer-Amazon
Properties:
  - Pretty Print JSON: true
  - Suppress Null Values: never
```

### **PostgreSQL Connection Pool**
```
Type: DBCPConnectionPool  
Name: PostgreSQL-Pool-Amazon
Properties:
  - Database Connection URL: jdbc:postgresql://postgres:5432/dw_nerds_prd
  - Database Driver Class Name: org.postgresql.Driver
  - Database User: postgres
  - Password: postgres
```

## 📁 **Arquivos Disponíveis para Teste**
```bash
# Dentro do container NiFi:
/opt/nifi/input/amazon/books_data.csv      (6 linhas)
/opt/nifi/input/amazon/Books_rating.csv    (6 linhas)
```

## 🐛 **Troubleshooting**

### **Se GetFile não processar arquivos:**
- Verificar permissões: `ls -la /opt/nifi/input/amazon/`
- Verificar configuração "Input Directory"
- Checar "Bulletin Board" para erros

### **Se LogMessage não mostrar logs:**
- Verificar se relationship "success" está conectada
- Verificar se LogMessage está "auto-terminated"
- Checar "Data Provenance" para rastreamento

### **Para ver logs detalhados:**
```bash
docker logs nifi --tail 20 -f
```

## 🎯 **Resultado Esperado**

Ao funcionar, você verá:
1. **GetFile**: Processa CSVs de `/opt/nifi/input/amazon/`  
2. **LogMessage**: Mostra "AMAZON_CSV_PROCESSED: filename.csv"
3. **Bulletin Board**: Sem erros, apenas informações
4. **Data Provenance**: Histórico de processamento

---

## 🚀 **COMECE AGORA**

**Ignore completamente os templates** - construa o flow manualmente seguindo este guia. É mais rápido e funciona 100%! ✅

**Primeiro objetivo**: GetFile → LogMessage funcionando
**Depois**: Expandir para processamento completo