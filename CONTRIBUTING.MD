## **Workflow Overview**

### **Step 1: Use Linear to Copy the Branch Name**
1. Open your assigned ticket in **Linear**.
2. Use the shortcut `CMD + Shift + .` to copy the branch name for the ticket. This will include the ticket code (e.g., `qingyu2555/is2-10-setup-springboot`).

---

### **Step 2: Create a New Branch**
1. Navigate to your local repository:
   ```bash
   cd /path/to/your/repository
   ```
2. Create and switch to a new branch using the Linear branch name:
   ```bash
   git checkout -b <branch-name>
   ```
   Replace `<branch-name>` with the name copied from Linear (e.g., `qingyu2555/is2-10-setup-springboot`).

---

### **Step 3: Make Changes**
1. Make the necessary changes to your codebase as described in the Linear ticket.
2. Test your changes locally to ensure they work as expected.

---

### **Step 4: Commit Your Changes**
1. Stage your changes:
2. Write a clear and concise commit message:
   ```bash
   git commit -m "Fix: Add login functionality (CMC-123)"
   ```

---

### **Step 5: Push the Branch**
Push your branch to the remote repository:
```bash
git push origin <branch-name>
```

---

### **Step 6: Create a Pull Request (PR)**
1. Open the repository on GitHub (or your preferred Git platform).
2. Create a new Pull Request (PR) from your branch into the main branch.
3. Include the following in the PR description:
    - A summary of the changes.
    - The Linear ticket code (e.g., `is2-10`).
    - Any relevant screenshots or details for context.

---

### **Step 7: Get Your PR Reviewed**
1. Request a team member to review your PR.
2. Address any feedback provided during the review process.

> **Note:** A review is optional but encouraged to maintain code quality and consistency.

---

### **Step 8: Merge the PR**
Once your PR is approved (if reviewed) or ready:
1. Merge the PR into the main branch.
2. Delete the feature branch after merging to keep the repository clean.

