#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdbool.h>

extern int next_thread_id;
extern int max_squares;
extern char ***dead_end_boards; /* do NOT free this memory in hw3.c */
int boardRows, boardCols = 0;
int deadEndThreshold;
int deadEndCount = 0;
pthread_t originThread;
/*
NOTE: check moves counter clockwise
*/

typedef struct
{
    //Or whatever information that you need
    int **board;
    int currentRow;
    int currentCol;
    int id;
    int current_squares;
} arguments;

typedef struct
{
    int id;
    int squares_covered;
} retarguments;

void printBoard(int **board)
{ // for debugging
    printf("\n");
    for (int i = 0; i <= boardRows; i++)
    {
        for (int j = 0; j <= boardCols; j++)
        {
            printf("%d", board[i][j]);
        }
        printf("\n");
    }
}
void makeNextMove(int *r, int *c, int movenum, int *current_squares, int **board)
{
    switch (movenum)
    {
    case 0:
        *r += 1;
        *c += 2;
        break;
    case 1:
        *r -= 1;
        *c += 2;
        break;
    case 2:
        *r -= 2;
        *c += 1;
        break;
    case 3:
        *r -= 2;
        *c -= 1;
        break;
    case 4:
        *r -= 1;
        *c -= 2;
        break;
    case 5:
        *r += 1;
        *c -= 2;
        break;
    case 6:
        *r += 2;
        *c -= 1;
        break;

    default:
        *r += 2;
        *c += 1;
        break;
    }
    if(*r > boardRows || *c > boardCols){
        fprintf(stderr, "Out of bound, r is %d, c is %d\n",*r, *c);
        return;
    }
    board[(int)*r][(int)*c] = *current_squares;
    (*current_squares) += 1;
}
int determineNextMove(int **board, int row, int col, int *moveCounter, int *lastMove)
{ // determine the next available move (in number)
    int counter = 0;
    int nextMove = -1;
    if (row + 1 <= boardRows && col + 2 <= boardCols && board[row + 1][col + 2] == -1)
    { // row+1, col+2,  movenum: 0
        counter++;
        if (*lastMove <= -1 && nextMove == -1)
        {
            nextMove = 0;
        }
    }

    if (row - 1 >= 0 && col + 2 <= boardCols && board[row - 1][col + 2] == -1)
    { // row-1, col+2, movenum:1
        counter++;
        if (*lastMove <= 0 && nextMove == -1)
        {
            nextMove = 1;
        }
    }

    if (row - 2 >= 0 && col + 1 <= boardCols && board[row - 2][col + 1] == -1)
    { // row-2, col+1, movenum:2
        counter++;
        if (*lastMove <= 1 && nextMove == -1)
        {
            nextMove = 2;
        }
    }

    if (row - 2 >= 0 && col - 1 >= 0 && board[row - 2][col - 1] == -1)
    { // row-2, col-1, movenum:3
        counter++;
        if (*lastMove <= 2 && nextMove == -1)
        {
            nextMove = 3;
        }
    }

    if (row - 1 >= 0 && col - 2 >= 0 && board[row - 1][col - 2] == -1)
    { // row-1, col-2, movenum:4
        counter++;
        if (*lastMove <= 3 && nextMove == -1)
        {
            nextMove = 4;
        }
    }

    if (row + 1 <= boardRows && col - 2 >= 0 && board[row + 1][col - 2] == -1)
    { // row+1, col-2, movenum:5
        counter++;
        if (*lastMove <= 4 && nextMove == -1)
        {
            nextMove = 5;
        }
    }

    if (row + 2 <= boardRows && col - 1 >= 0 && board[row + 2][col - 1] == -1)
    { // row+2, col-1, movenum:6
        counter++;
        if (*lastMove <= 5 && nextMove == -1)
        {
            nextMove = 6;
        }
    }
    if (row + 2 <= boardRows && col + 1 <= boardCols && board[row + 2][col + 1] == -1)
    { // row+2, col+1, movenum:7
        counter++;
        if (*lastMove <= 6 && nextMove == -1)
        {
            nextMove = 7;
        }
    }

    *moveCounter = counter;
    *lastMove = nextMove;
    return nextMove;
}

void *findNextMove(void *ar)
{ // find the nextpossible move based on parameters passed in
    arguments *a = ar;
    int **board = a->board;
    int currentRow = a->currentRow;
    int currentCol = a->currentCol;
    int thread_id = a->id;
    int current_squares = a->current_squares;
    int moveCounter = 0; // keeps track of how many moves are available given the current board state and position
    int lastMove = -1;
    int *ret = calloc(1, sizeof(int));
    arguments *args = malloc(sizeof *args);

    int next = determineNextMove(board, currentRow, currentCol, &moveCounter, &lastMove);

    if (moveCounter == 0)
    { // deal with dead end board

        free(args);
        printf("thread %d is deadend\n",thread_id);
        if (current_squares < deadEndThreshold)
        { // free the board if covered squares is lower than threshold
            // for (int i = 0; i <= boardRows; i++)
            // {
            //     free(board[i]);
            // }
            // free(board);
            printf("\nDEAD END");
            printf("cur pos: (%d,%d), next is %d", currentRow, currentCol, next);
            printBoard(board);
            
        }
        else if (current_squares == (boardRows + 1) * (boardCols + 1) - 1)
        { // solution is found
           
        }
        else
        { // update dead end boards with new dead end board
            // dead_end_boards[deadEndCount] = calloc(boardRows + 1, sizeof(char *));
            // for (int i = 0; i <= boardRows; i++)
            // {
            //     dead_end_boards[deadEndCount][i] = calloc(boardCols + 1, sizeof(char));
            //     for (int j = 0; j <= boardCols; j++)
            //     {
            //         if (board[i][j] != -1)
            //             dead_end_boards[deadEndCount][i][j] = 'S';
            //         else
            //             dead_end_boards[deadEndCount][i][j] = '.';
            //     }
            // }
            // deadEndCount++;
            printf("\nvery dead\n");
            
            
        }
        *ret = current_squares;
        pthread_exit(ret);
        // exit the function & report back to its parent thread the squares it covered
    }
    else if (moveCounter < 0)
    {
        fprintf(stderr, "Something wrong with movecounter.");
    }
    else if (moveCounter == 1)
    { // don't create new thread continue on this thread til find multiple available moves
        makeNextMove(&currentRow, &currentCol, next, &current_squares, board);
        arguments *newArgs = malloc(sizeof *newArgs);
        newArgs->board = board;
        newArgs->currentRow = currentRow;
        newArgs->currentCol = currentCol;
        newArgs->current_squares= current_squares;
        newArgs->id = thread_id;
        printf("(%d,%d), next move is %d, thread is %d\n", currentRow, currentCol, next,thread_id);
        findNextMove(newArgs);
    }
    else
    { // create new thread
        pthread_t tids[8];
        for (int i = 0; i < 8; i++)
        {
            tids[i] = -1;
        }
        int tidCounter = 0;
        int n = next;
        while (n != -1)
        {
            int error;
            // makeNextMove(&currentRow, &currentCol, n, &current_squares, board);
            printf("n is %d, thread is %ld\n", n, pthread_self());
            int **duplicateboard = calloc(boardRows + 1, sizeof(int *));
            for (int i = 0; i <= boardRows; i++)
            {
                duplicateboard[i] = calloc(boardCols + 1, sizeof(int));
                for (int j = 0; j <= boardCols; j++)
                {
                    duplicateboard[i][j] = board[i][j];
                }
            }
            // critical section begins
            args->board = duplicateboard;
            args->currentCol = currentCol;
            args->currentRow = currentRow;
            args->id = next_thread_id;
            args->current_squares = current_squares+1;
            makeNextMove(&args->currentRow, &args->currentCol, n, &args->current_squares, args->board);
            printf("current position: (%d, %d)\n", args->currentRow, args->currentCol);
            printf("\n");
            error = pthread_create(&(tids[tidCounter]),
                                   NULL,
                                   &findNextMove, args);
            if (error != 0)
            {
                fprintf(stderr, "ERROR: Thread can't be created");
            }
            n = determineNextMove(board, currentRow, currentCol, &moveCounter, &lastMove);
            tidCounter++;
            next_thread_id++;
            //critical section ends
        }
        printf("current thread is %ld\n",pthread_self());
#ifndef NO_PARALLEL
        for (int i = 0; i < tidCounter; i++)
        {
            printf("THREAD %ldwants to join\n", tids[i]);
            if (tids[tidCounter] != -1)
            {
                void *retFromChild = malloc(0);
                free(retFromChild);
                pthread_join(tids[tidCounter], (void**)&retFromChild);
                int potentialHigh = *(int *)retFromChild;
                if (potentialHigh > max_squares)
                {
                    max_squares = potentialHigh;
                }
                printf("THREAD %ld JOINED\n", pthread_self());
            }
        }
#endif
    }
}
int simulate(int argc, char *argv[])
{
    if (argc != 6)
    {
        fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c> <x>");
        return EXIT_FAILURE;
    }
    setvbuf(stdout, NULL, _IONBF, 0);
    int rows = atoi(argv[1]);
    int cols = atoi(argv[2]);
    boardRows = rows - 1;
    boardCols = cols - 1;
    int startingRow = atoi(argv[3]);
    int startingCol = atoi(argv[4]);
    deadEndThreshold = atoi(argv[5]); // only store dead end boards with at least this threshold squares covered
    if (rows < 2 || cols < 2 || startingRow >= rows || startingCol >= cols || startingRow < 0 || startingCol < 0 || deadEndThreshold > rows * cols)
    {
        fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c> <x>");
        return EXIT_FAILURE;
    }

    int **board = calloc(rows, sizeof(int *));
    for (int i = 0; i < rows; i++)
    {
        board[i] = calloc(cols, sizeof(int));
        for (int j = 0; j < cols; j++)
        {
            board[i][j] = -1; // initialize every square to -1
        }
    }

    board[startingRow][startingCol] = 0; // set initial position to 0

    arguments *a = malloc(sizeof *a);
    a->board = board;
    a->currentRow = startingRow;
    a->currentCol = startingCol;
    a->id = next_thread_id;
    a->current_squares = 1;

    findNextMove(a);
    originThread = pthread_self();
    // start checking surrounding positions

    return EXIT_SUCCESS;
}