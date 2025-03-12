from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset

# Step 1: Load Dataset
dataset = load_dataset("json", data_files={"train": "train.jsonl"})  # Load your dataset from train.jsonl

# Step 2: Load Model & Tokenizer
model_name = "microsoft/phi-1_5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")  # Removed load_in_8bit

# Step 3: Apply LoRA Fine-Tuning
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,  # Causal Language Model Task
    r=8, 
    lora_alpha=32, 
    lora_dropout=0.05
)
model = get_peft_model(model, lora_config)

# Step 4: Tokenize Dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Step 5: Training Setup
training_args = TrainingArguments(
    output_dir="./mistral_finetuned",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    report_to="none"
)

# Step 6: Train the Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"]
)

trainer.train()


model.save_pretrained("./phi_finetuned")
tokenizer.save_pretrained("./phi_finetuned")
